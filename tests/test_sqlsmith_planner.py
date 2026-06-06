import pytest

from sqlsmith.planner import plan_candidates
from sqlsmith.schema import normalize_schema
from sqlsmith.task import SQLTask


BASIC_SCHEMA = {
    "customers": ["id", "name", "email", "city", "phone", "created_at"],
    "orders": ["id", "customer_id", "order_date", "total", "status"],
}


@pytest.mark.parametrize(
    ("question", "expected_sql"),
    [
        (
            "Count the total number of customers in the database",
            "SELECT COUNT(*) AS total FROM customers",
        ),
        (
            "Find all customers who live in New York",
            "SELECT * FROM customers WHERE city = 'New York'",
        ),
        (
            "Get customer names along with their order dates and totals",
            "SELECT c.name, o.order_date, o.total FROM customers AS c JOIN orders AS o ON c.id = o.customer_id",
        ),
        (
            "Count the number of customers in each city, ordered by count descending",
            "SELECT city, COUNT(*) AS customer_count FROM customers GROUP BY city ORDER BY customer_count DESC",
        ),
        (
            "Calculate the total revenue from all orders",
            "SELECT SUM(total) AS total_revenue FROM orders",
        ),
        (
            "Calculate the average order value",
            "SELECT AVG(total) AS avg_order_value FROM orders",
        ),
        (
            "Get a list of all unique cities where customers live",
            "SELECT DISTINCT city FROM customers ORDER BY city",
        ),
        (
            "Get the 3 most recent orders based on order date",
            "SELECT * FROM orders ORDER BY order_date DESC LIMIT 3",
        ),
        (
            "Get customer names and phone numbers, showing 'N/A' for missing phone numbers",
            "SELECT name, COALESCE(phone, 'N/A') AS phone FROM customers",
        ),
        (
            "Find orders with totals between 50 and 200 (inclusive)",
            "SELECT * FROM orders WHERE total BETWEEN 50 AND 200",
        ),
        (
            "Get all customers and their orders (including customers with no orders)",
            "SELECT c.name, o.total FROM customers AS c LEFT JOIN orders AS o ON c.id = o.customer_id",
        ),
        (
            "Find customers who have placed orders with a total greater than 100",
            "SELECT * FROM customers WHERE id IN (SELECT customer_id FROM orders WHERE total > 100)",
        ),
        (
            "Categorize orders as 'high', 'medium', or 'low' based on total amount",
            "SELECT id, total, CASE WHEN total > 500 THEN 'high' WHEN total > 100 THEN 'medium' ELSE 'low' END AS category FROM orders",
        ),
        (
            "Get customer names in uppercase along with the length of their names",
            "SELECT UPPER(name) AS upper_name, LENGTH(name) AS name_length FROM customers",
        ),
    ],
)
def test_public_basic_fixture_patterns(question, expected_sql):
    task = SQLTask(
        task_id=None,
        question=question,
        schema=BASIC_SCHEMA,
        dialect="sqlite",
    )

    candidates = plan_candidates(task, normalize_schema(task.schema))

    assert candidates
    assert candidates[0].sql == expected_sql
