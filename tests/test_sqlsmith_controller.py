from sqlsmith.controller import SQLSmithController


BASIC_SCHEMA = {
    "customers": ["id", "name", "email", "city", "phone", "created_at"],
    "orders": ["id", "customer_id", "order_date", "total", "status"],
}


def test_controller_returns_agentbeats_sql_payload():
    result = SQLSmithController().solve(
        {
            "task_id": "sqlite_count",
            "question": "Count the total number of customers in the database",
            "schema": BASIC_SCHEMA,
            "dialect": "sqlite",
        }
    )

    assert result["task_id"] == "sqlite_count"
    assert result["sql"] == "SELECT COUNT(*) AS total FROM customers"
    assert "strategy=customer_count" in result["reasoning"]


def test_controller_never_raises_for_missing_question():
    result = SQLSmithController().solve({"task_id": "bad"})

    assert result["task_id"] == "bad"
    assert result["sql"] == ""
    assert "missing question" in result["reasoning"]

