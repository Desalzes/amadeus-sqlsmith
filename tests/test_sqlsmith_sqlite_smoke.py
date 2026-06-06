import sqlite3

from sqlsmith.controller import SQLSmithController


BASIC_SCHEMA = {
    "customers": ["id", "name", "email", "city", "phone", "created_at"],
    "orders": ["id", "customer_id", "order_date", "total", "status"],
}


def test_generated_sql_matches_representative_sqlite_fixture_results():
    conn = _fixture_connection()
    controller = SQLSmithController()

    cases = [
        (
            "Count the total number of customers in the database",
            [{"total": 5}],
        ),
        (
            "Calculate the total revenue from all orders",
            [{"total_revenue": 1675.5}],
        ),
        (
            "Calculate the average order value",
            [{"avg_order_value": 335.1}],
        ),
        (
            "Count the number of customers in each city, ordered by count descending",
            [
                {"city": "New York", "customer_count": 2},
                {"city": "San Francisco", "customer_count": 1},
                {"city": "Los Angeles", "customer_count": 1},
                {"city": "Chicago", "customer_count": 1},
            ],
        ),
        (
            "Get a list of all unique cities where customers live",
            [
                {"city": "Chicago"},
                {"city": "Los Angeles"},
                {"city": "New York"},
                {"city": "San Francisco"},
            ],
        ),
        (
            "Get customer names and phone numbers, showing 'N/A' for missing phone numbers",
            [
                {"name": "Alice Johnson", "phone": "555-0101"},
                {"name": "Bob Smith", "phone": "555-0102"},
                {"name": "Charlie Brown", "phone": "555-0103"},
                {"name": "Diana Ross", "phone": "555-0104"},
                {"name": "Edward Kim", "phone": "N/A"},
            ],
        ),
    ]

    for question, expected in cases:
        result = controller.solve({"question": question, "schema": BASIC_SCHEMA})
        assert _query(conn, result["sql"]) == expected


def _fixture_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            city TEXT,
            phone TEXT,
            created_at TEXT
        );
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date TEXT,
            total REAL,
            status TEXT
        );
        """
    )
    conn.executemany(
        "INSERT INTO customers (id, name, email, city, phone, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        [
            (1, "Alice Johnson", "alice@example.com", "New York", "555-0101", "2024-01-01"),
            (2, "Bob Smith", "bob@example.com", "Los Angeles", "555-0102", "2024-01-01"),
            (3, "Charlie Brown", "charlie@example.com", "Chicago", "555-0103", "2024-01-01"),
            (4, "Diana Ross", "diana@example.com", "New York", "555-0104", "2024-01-01"),
            (5, "Edward Kim", "edward@example.com", "San Francisco", None, "2024-01-01"),
        ],
    )
    conn.executemany(
        "INSERT INTO orders (id, customer_id, order_date, total, status) VALUES (?, ?, ?, ?, ?)",
        [
            (1, 1, "2024-01-15", 150.00, "completed"),
            (2, 1, "2024-02-20", 75.50, "completed"),
            (3, 2, "2024-01-25", 200.00, "completed"),
            (4, 3, "2024-03-01", 50.00, "pending"),
            (5, 4, "2024-03-10", 1200.00, "completed"),
        ],
    )
    return conn


def _query(conn: sqlite3.Connection, sql: str) -> list[dict[str, object]]:
    rows = conn.execute(sql).fetchall()
    return [dict(row) for row in rows]
