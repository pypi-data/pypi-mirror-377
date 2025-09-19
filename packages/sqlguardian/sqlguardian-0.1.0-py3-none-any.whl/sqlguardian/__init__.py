"""SQLGuardian."""

from __future__ import annotations

__all__: tuple[str, ...] = (
    "SQL",
    "AllowedTableInfo",
    "AllowlistError",
    "ColumnName",
    "DatabaseName",
    "DbRule",
    "Description",
    "Policy",
    "TableAlias",
    "TableName",
    "TableRule",
    "describe_allowed_tables",
    "enforce_policy_where_guards",
    "render_markdown_description",
)

from typing import TYPE_CHECKING, Self, TypedDict

import yaml
from pydantic import BaseModel, Field
from sqlglot import exp, parse_one

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path

# ============================================================================
# Domain type aliases (Python 3.13 style)
# ============================================================================

type DatabaseName = str
type TableName = str
type TableAlias = str
type ColumnName = str
type Description = str
type SQL = str


# TypedDict describing each row returned by describe_allowed_tables
class AllowedTableInfo(TypedDict):
    """Describes one allowlisted table."""

    database: DatabaseName
    table: TableName
    guard_column: ColumnName
    description: Description


# ============================================================================
# Exceptions
# ============================================================================


class AllowlistError(PermissionError):
    """Raised when a referenced (db, table) is not allowlisted."""


# ============================================================================
# Pydantic models for YAML policy
# ============================================================================


class TableRule(BaseModel):
    """Rules for one table."""

    guard_column: ColumnName | None = None
    description: Description | None = None


class DbRule(BaseModel):
    """Rules for one database."""

    guard_column: ColumnName | None = None
    tables: dict[TableName, TableRule] = Field(default_factory=dict)


class Policy(BaseModel):
    """The overall multi-tenant policy."""

    default_guard_column: ColumnName | None = None
    databases: dict[DatabaseName, DbRule] = Field(default_factory=dict)

    # ------------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------------
    @classmethod
    def from_yaml(cls, path: Path) -> Self:
        """Load a Policy from a YAML file."""
        with path.open(encoding="utf-8") as f:
            return cls.model_validate(yaml.safe_load(f) or {})

    # ------------------------------------------------------------------------
    # Runtime helpers
    # ------------------------------------------------------------------------
    def is_allowed(self, db: DatabaseName | None, table: TableName) -> bool:
        """Is this (db, table) allowlisted?"""
        db_key = db or "default"
        return db_key in self.databases and table in self.databases[db_key].tables

    def guard_column_for(self, db: DatabaseName | None, table: TableName) -> ColumnName:
        """Get the guard column for this (db, table).

        Raises AllowlistError if not allowlisted.
        """
        db_key = db or "default"
        db_rule = self.databases.get(db_key)
        if not db_rule:
            msg = f"Database '{db_key}' not allowlisted"
            raise AllowlistError(msg)
        tbl_rule = db_rule.tables.get(table)
        if not tbl_rule:
            msg = f"Table '{db_key}.{table}' not allowlisted"
            raise AllowlistError(msg)
        return (
            tbl_rule.guard_column
            or db_rule.guard_column
            or self.default_guard_column
            or "companyId"
        )

    def table_description(
        self,
        db: DatabaseName | None,
        table: TableName,
    ) -> Description | None:
        """Get the human/LLM description for this (db, table), if any."""
        db_key = db or "default"
        return (
            self.databases.get(db_key, DbRule())
            .tables.get(table, TableRule())
            .description
        )


# ============================================================================
# SQL utilities
# ============================================================================


def _table_alias(t: exp.Table) -> TableAlias | None:
    alias = t.args.get("alias")
    if isinstance(alias, exp.TableAlias):
        ident = alias.args.get("this")
        if isinstance(ident, exp.Identifier):
            return ident.name
    return None


def _table_name(t: exp.Table) -> TableName:
    ident = t.args.get("this")
    return ident.name if isinstance(ident, exp.Identifier) else str(ident)


def _db_name(t: exp.Table) -> DatabaseName | None:
    db = t.args.get("db")
    return db.name if isinstance(db, exp.Identifier) else None


def _predicate_exists(where_expr: exp.Where | None, pred: exp.Expression) -> bool:
    if not where_expr:
        return False
    target = pred.sql(dialect="clickhouse")
    return any(
        eq.sql(dialect="clickhouse") == target for eq in where_expr.find_all(exp.EQ)
    )


def _and_where(select: exp.Select, extra_predicates: list[exp.Expression]) -> None:
    if not extra_predicates:
        return
    combined = extra_predicates[0]
    for p in extra_predicates[1:]:
        combined = exp.and_(combined, p)
    existing = select.args.get("where")
    select.set(
        "where",
        exp.Where(this=exp.and_(existing.this, combined) if existing else combined),
    )


# ============================================================================
# Core enforcement
# ============================================================================


def enforce_policy_where_guards(
    sql: SQL,
    *,
    company_value: str,
    policy: Policy,
    read_dialect: str = "clickhouse",
    write_dialect: str = "clickhouse",
) -> SQL:
    """Enforce the multi-tenant policy on the given SQL query.

    - Validates that every referenced (db, table) is allowlisted.
    - Adds WHERE `<alias>.<guard_col> = <company_value>` for each referenced table
      in every SELECT (joins, subqueries, CTEs included).
    - Skips adding a predicate if an identical one already exists.
    """
    root = parse_one(sql, read=read_dialect)

    # Check all tables first
    for t in root.find_all(exp.Table):
        db, tbl = _db_name(t), _table_name(t)
        if not policy.is_allowed(db, tbl):
            db_key = db or "default"
            msg = f"Reference to non-allowlisted table: {db_key}.{tbl}"
            raise AllowlistError(msg)

    # Add guards
    for sel in root.find_all(exp.Select):
        tables = list(sel.find_all(exp.Table))
        if not tables:
            continue
        predicates: list[exp.Expression] = []
        for t in tables:
            db, tbl = _db_name(t), _table_name(t)
            guard_col = policy.guard_column_for(db, tbl)
            qualifier: TableAlias | TableName = _table_alias(t) or tbl
            pred = exp.EQ(
                this=exp.column(guard_col, table=qualifier),
                expression=exp.Literal.string(company_value),
            )
            if not _predicate_exists(sel.args.get("where"), pred):
                predicates.append(pred)
        _and_where(sel, predicates)

    return root.sql(dialect=write_dialect)


# ============================================================================
# Human/LLM descriptions of the allowlist
# ============================================================================


def describe_allowed_tables(policy: Policy) -> list[AllowedTableInfo]:
    """Describe the allowlisted tables in the policy.

    Return a list of AllowedTableInfo dicts describing every allowed table.
    """
    rows: list[AllowedTableInfo] = []
    for db_name, db_rule in sorted(policy.databases.items()):
        rows.extend(
            AllowedTableInfo(
                database=db_name,
                table=tbl_name,
                guard_column=(
                    tbl_rule.guard_column
                    or db_rule.guard_column
                    or policy.default_guard_column
                    or "companyId"
                ),
                description=tbl_rule.description or "",
            )
            for tbl_name, tbl_rule in sorted(db_rule.tables.items())
        )
    return rows


def render_markdown_description(policy: Policy) -> str:
    """Pretty Markdown table of all allowed tables for documentation or LLM priming."""
    rows = describe_allowed_tables(policy)
    lines: list[str] = [
        "### Allowed Tables",
        "",
        "| Database | Table | Guard Column | Description |",
        "|---|---|---|---|",
    ]
    for r in rows:
        desc = r["description"].replace("\n", " ").strip()
        lines.append(
            f"| `{r['database']}` | `{r['table']}` | `{r['guard_column']}` | {desc} |"
        )
    return "\n".join(lines)
