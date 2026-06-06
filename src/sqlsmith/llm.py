from __future__ import annotations

import os

from .schema import SchemaCatalog
from .task import SQLTask, extract_sql


class OptionalOpenAIPlanner:
    def __init__(self, model: str | None = None):
        self.model = model or os.environ.get("SQLSMITH_OPENAI_MODEL", "gpt-5-mini")

    def generate(self, task: SQLTask, schema: SchemaCatalog) -> str | None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return None

        try:
            from openai import OpenAI
        except ImportError:
            return None

        schema_text = "\n".join(
            f"{table}: {', '.join(schema.column_names(table))}"
            for table in schema.table_names()
        )
        client = OpenAI(api_key=api_key)
        try:
            response = client.chat.completions.create(
                model=self.model,
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": "Return only one safe SELECT SQL query for the requested dialect.",
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Dialect: {task.dialect}\nSchema:\n{schema_text}\n\n"
                            f"Question: {task.question}"
                        ),
                    },
                ],
            )
        except Exception:
            return None
        text = response.choices[0].message.content or ""
        return extract_sql(text) or None
