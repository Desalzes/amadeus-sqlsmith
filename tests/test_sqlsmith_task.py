import json

from sqlsmith.task import SQLTask, extract_sql, parse_task_payload


def test_parse_json_task_payload():
    task = parse_task_payload(
        json.dumps(
            {
                "task_id": "sqlite_count",
                "question": "Count the total number of customers in the database",
                "schema": {"customers": ["id", "name"]},
                "dialect": "sqlite",
            }
        )
    )

    assert task == SQLTask(
        task_id="sqlite_count",
        question="Count the total number of customers in the database",
        schema={"customers": ["id", "name"]},
        dialect="sqlite",
    )


def test_parse_plain_text_as_question():
    task = parse_task_payload("Count customers")

    assert task.task_id is None
    assert task.question == "Count customers"
    assert task.schema == {}
    assert task.dialect == "sqlite"


def test_extract_sql_from_code_fence_and_plain_text():
    assert extract_sql("```sql\nSELECT COUNT(*) FROM customers;\n```") == (
        "SELECT COUNT(*) FROM customers;"
    )
    assert extract_sql("The answer is:\nSELECT * FROM orders LIMIT 3;") == (
        "SELECT * FROM orders LIMIT 3;"
    )

