from __future__ import annotations

from dataclasses import dataclass
import re

from .schema import SchemaCatalog


@dataclass(frozen=True)
class ValidationReport:
    ok: bool
    errors: list[str]


def validate_sql(sql: str, schema: SchemaCatalog, dialect: str = "sqlite") -> ValidationReport:
    errors: list[str] = []
    stripped = sql.strip().rstrip(";")
    if not re.match(r"^(select|with)\b", stripped, flags=re.IGNORECASE):
        errors.append("only SELECT statements are allowed")

    try:
        import sqlglot
        from sqlglot import exp

        parsed = sqlglot.parse_one(stripped, read=_sqlglot_dialect(dialect))
        if not isinstance(parsed, (exp.Select, exp.Subquery, exp.Union)) and not parsed.find(exp.Select):
            errors.append("only SELECT statements are allowed")

        aliases: dict[str, str] = {}
        referenced_tables: set[str] = set()
        for table in parsed.find_all(exp.Table):
            table_name = table.name
            referenced_tables.add(table_name.lower())
            aliases[table.alias_or_name.lower()] = table_name.lower()
            if not schema.has_table(table_name):
                errors.append(f"phantom table: {table_name}")

        projection_aliases = {
            expression.alias.lower()
            for expression in parsed.expressions
            if getattr(expression, "alias", "")
        }

        for column in parsed.find_all(exp.Column):
            column_name = column.name
            if column_name == "*" or column_name.lower() in projection_aliases:
                continue
            table_name = column.table
            if table_name:
                real_table = aliases.get(table_name.lower(), table_name.lower())
                if schema.has_table(real_table) and not schema.has_column(real_table, column_name):
                    errors.append(f"phantom column: {column_name}")
                elif not schema.has_table(real_table):
                    errors.append(f"phantom table: {real_table}")
            elif not _column_exists_in_referenced_tables(column_name, referenced_tables, schema):
                errors.append(f"phantom column: {column_name}")
    except Exception:
        errors.extend(_fallback_identifier_errors(stripped, schema))

    return ValidationReport(ok=not errors, errors=_dedupe(errors))


def _sqlglot_dialect(dialect: str) -> str:
    if dialect in {"sqlite", "duckdb", "postgres", "postgresql", "bigquery"}:
        return "postgres" if dialect == "postgresql" else dialect
    return "sqlite"


def _column_exists_in_referenced_tables(column: str, tables: set[str], schema: SchemaCatalog) -> bool:
    if not tables:
        return schema.find_table_for_column(column) is not None
    return any(schema.has_column(table, column) for table in tables)


def _fallback_identifier_errors(sql: str, schema: SchemaCatalog) -> list[str]:
    errors: list[str] = []
    table_matches = re.findall(r"\b(?:from|join)\s+([A-Za-z_][A-Za-z0-9_]*)", sql, flags=re.IGNORECASE)
    for table_name in table_matches:
        if not schema.has_table(table_name):
            errors.append(f"phantom table: {table_name}")

    select_match = re.search(r"\bselect\s+(.*?)\s+from\b", sql, flags=re.IGNORECASE | re.DOTALL)
    if select_match:
        for raw in select_match.group(1).split(","):
            token = raw.strip().split()[0]
            if token == "*" or "(" in token:
                continue
            column = token.split(".")[-1]
            if schema.find_table_for_column(column) is None:
                errors.append(f"phantom column: {column}")
    return errors


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result
