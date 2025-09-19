"""Unit tests for sqlguardian."""

import pytest

from sqlguardian import (
    AllowlistError,
    Policy,
    describe_allowed_tables,
    enforce_policy_where_guards,
    render_markdown_description,
)


def make_policy() -> Policy:
    """Create a sample Policy for testing."""
    return Policy.model_validate(
        {
            "default_guard_column": "companyId",
            "databases": {
                "default": {
                    "guard_column": "companyId",
                    "tables": {
                        "users": {"description": "User table"},
                        "orders": {
                            "guard_column": "orgId",
                            "description": "Order table",
                        },
                    },
                },
                "analytics": {
                    "guard_column": "tenantId",
                    "tables": {
                        "events": {"description": "Event log"},
                    },
                },
            },
        }
    )


def test_policy_is_allowed() -> None:
    """Test Policy.is_allowed for various cases."""
    policy = make_policy()
    assert policy.is_allowed(None, "users")
    assert policy.is_allowed("default", "orders")
    assert policy.is_allowed("analytics", "events")
    assert not policy.is_allowed("default", "missing")
    assert not policy.is_allowed("unknown", "users")


def test_policy_guard_column_for() -> None:
    """Test Policy.guard_column_for returns correct guard column."""
    policy = make_policy()
    assert policy.guard_column_for(None, "users") == "companyId"
    assert policy.guard_column_for("default", "orders") == "orgId"
    assert policy.guard_column_for("analytics", "events") == "tenantId"


def test_policy_guard_column_for_error() -> None:
    """Test Policy.guard_column_for raises AllowlistError for missing tables."""
    policy = make_policy()
    with pytest.raises(AllowlistError):
        policy.guard_column_for("default", "missing")
    with pytest.raises(AllowlistError):
        policy.guard_column_for("unknown", "users")


def test_policy_table_description() -> None:
    """Test Policy.table_description returns correct descriptions."""
    policy = make_policy()
    assert policy.table_description(None, "users") == "User table"
    assert policy.table_description("default", "orders") == "Order table"
    assert policy.table_description("analytics", "events") == "Event log"
    assert policy.table_description("default", "missing") is None


def test_enforce_policy_where_guards_adds_predicate() -> None:
    """Test enforcement adds guard predicate to SQL."""
    policy = make_policy()
    sql = "SELECT * FROM users"
    out = enforce_policy_where_guards(sql, company_value="42", policy=policy)
    assert "WHERE users.companyId = '42'" in out


def test_enforce_policy_where_guards_existing_predicate() -> None:
    """Test enforcement does not duplicate existing predicate."""
    policy = make_policy()
    sql = "SELECT * FROM users WHERE users.companyId = '42'"
    out = enforce_policy_where_guards(sql, company_value="42", policy=policy)
    # Should not duplicate predicate
    assert out.count("users.companyId = '42'") == 1


def test_enforce_policy_where_guards_non_allowlisted() -> None:
    """Test enforcement raises AllowlistError for non-allowlisted tables."""
    policy = make_policy()
    sql = "SELECT * FROM missing"
    with pytest.raises(AllowlistError):
        enforce_policy_where_guards(sql, company_value="42", policy=policy)


def test_describe_allowed_tables() -> None:
    """Test describe_allowed_tables returns all allowed tables."""
    policy = make_policy()
    rows = describe_allowed_tables(policy)
    assert any(r["table"] == "users" for r in rows)
    assert any(r["table"] == "orders" for r in rows)
    assert any(r["table"] == "events" for r in rows)


def test_render_markdown_description() -> None:
    """Test render_markdown_description outputs correct markdown."""
    policy = make_policy()
    md = render_markdown_description(policy)
    assert "| Database | Table | Guard Column | Description |" in md
    assert "`default`" in md
    assert "`users`" in md
