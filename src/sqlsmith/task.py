from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any


@dataclass(frozen=True)
class SQLTask:
    task_id: str | None
    question: str
    schema: dict[str, Any]
    dialect: str = "sqlite"


def parse_task_payload(payload: Any) -> SQLTask:
    data = _coerce_payload(payload)
    if not isinstance(data, dict):
        return SQLTask(task_id=None, question=str(data).strip(), schema={}, dialect="sqlite")

    return SQLTask(
        task_id=data.get("task_id") or data.get("id"),
        question=str(data.get("question") or data.get("prompt") or "").strip(),
        schema=data.get("schema") or data.get("schema_info") or {},
        dialect=str(data.get("dialect") or "sqlite").lower(),
    )


def extract_sql(text: str) -> str:
    fenced = re.search(r"```(?:sql)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if fenced:
        return fenced.group(1).strip()

    statement = re.search(r"\b(WITH|SELECT)\b.*?(?:;|$)", text, flags=re.IGNORECASE | re.DOTALL)
    if statement:
        return statement.group(0).strip()

    return text.strip()


def _coerce_payload(payload: Any) -> Any:
    if isinstance(payload, SQLTask):
        return {
            "task_id": payload.task_id,
            "question": payload.question,
            "schema": payload.schema,
            "dialect": payload.dialect,
        }

    if isinstance(payload, dict):
        if "parts" in payload:
            from_parts = _coerce_parts(payload.get("parts") or [])
            if from_parts:
                return from_parts
        return payload

    if isinstance(payload, str):
        text = payload.strip()
        if not text:
            return {}
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text

    return payload


def _coerce_parts(parts: list[Any]) -> Any:
    for part in parts:
        if not isinstance(part, dict):
            continue
        if "data" in part:
            return part["data"]
        if part.get("type") == "data":
            return part.get("data") or {}
        text = part.get("text")
        if text:
            return _coerce_payload(text)
    return None
