from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Column:
    name: str
    type: str | None = None


@dataclass(frozen=True)
class Table:
    name: str
    columns: tuple[Column, ...]


@dataclass(frozen=True)
class SchemaCatalog:
    tables: dict[str, Table]

    def table_names(self) -> list[str]:
        return list(self.tables.keys())

    def has_table(self, name: str) -> bool:
        return name.lower() in self.tables

    def column_names(self, table: str) -> list[str]:
        found = self.tables.get(table.lower())
        if not found:
            return []
        return [column.name for column in found.columns]

    def has_column(self, table: str, column: str) -> bool:
        return column.lower() in {name.lower() for name in self.column_names(table)}

    def find_table_for_column(self, column: str) -> str | None:
        column_l = column.lower()
        matches = [
            table.name
            for table in self.tables.values()
            if column_l in {c.name.lower() for c in table.columns}
        ]
        return matches[0] if len(matches) == 1 else None


def normalize_schema(schema: dict[str, Any] | None) -> SchemaCatalog:
    schema = schema or {}
    raw_tables = schema.get("tables") if isinstance(schema.get("tables"), dict) else schema
    tables: dict[str, Table] = {}

    if isinstance(raw_tables, dict):
        for table_name, table_info in raw_tables.items():
            if not isinstance(table_name, str):
                continue
            columns = _extract_columns(table_info)
            table = Table(name=table_name, columns=tuple(columns))
            tables[table_name.lower()] = table

    return SchemaCatalog(tables=tables)


def _extract_columns(table_info: Any) -> list[Column]:
    if isinstance(table_info, dict):
        raw_columns = table_info.get("columns", [])
    else:
        raw_columns = table_info

    columns: list[Column] = []
    if isinstance(raw_columns, list):
        for column in raw_columns:
            if isinstance(column, dict):
                name = column.get("name") or column.get("column_name")
                if name:
                    columns.append(Column(name=str(name), type=column.get("type")))
            elif isinstance(column, str):
                columns.append(Column(name=column))
    elif isinstance(raw_columns, dict):
        for name, type_name in raw_columns.items():
            columns.append(Column(name=str(name), type=str(type_name)))
    elif isinstance(raw_columns, str):
        columns.append(Column(name=raw_columns))

    return columns
