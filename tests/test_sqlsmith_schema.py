from sqlsmith.schema import normalize_schema


def test_normalize_simple_schema_mapping():
    catalog = normalize_schema({"customers": ["id", "name", "city"]})

    assert catalog.table_names() == ["customers"]
    assert catalog.has_table("customers")
    assert catalog.has_column("customers", "city")
    assert catalog.find_table_for_column("name") == "customers"


def test_normalize_green_schema_tables_shape():
    catalog = normalize_schema(
        {
            "tables": {
                "orders": {
                    "columns": [
                        {"name": "id", "type": "INTEGER"},
                        {"name": "total", "type": "REAL"},
                    ]
                }
            }
        }
    )

    assert catalog.table_names() == ["orders"]
    assert catalog.column_names("orders") == ["id", "total"]

