from sqlsmith.schema import normalize_schema
from sqlsmith.validator import validate_sql


BASIC_SCHEMA = {
    "customers": ["id", "name", "email", "city", "phone", "created_at"],
    "orders": ["id", "customer_id", "order_date", "total", "status"],
}


def test_validate_accepts_safe_select():
    report = validate_sql(
        "SELECT city, COUNT(*) AS customer_count FROM customers GROUP BY city",
        normalize_schema(BASIC_SCHEMA),
        dialect="sqlite",
    )

    assert report.ok
    assert report.errors == []


def test_validate_rejects_phantom_table_and_column():
    report = validate_sql(
        "SELECT fake_column FROM missing_table",
        normalize_schema(BASIC_SCHEMA),
        dialect="sqlite",
    )

    assert not report.ok
    assert "phantom table: missing_table" in report.errors
    assert "phantom column: fake_column" in report.errors


def test_validate_rejects_non_select_statement():
    report = validate_sql(
        "DELETE FROM customers",
        normalize_schema(BASIC_SCHEMA),
        dialect="sqlite",
    )

    assert not report.ok
    assert "only SELECT statements are allowed" in report.errors

