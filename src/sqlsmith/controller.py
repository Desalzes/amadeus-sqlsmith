from __future__ import annotations

from typing import Any

from .llm import OptionalOpenAIPlanner
from .planner import Candidate, plan_candidates
from .schema import normalize_schema
from .task import parse_task_payload
from .validator import validate_sql


class SQLSmithController:
    def __init__(self, llm: OptionalOpenAIPlanner | None = None):
        self.llm = llm or OptionalOpenAIPlanner()

    def solve(self, payload: Any) -> dict[str, Any]:
        task = parse_task_payload(payload)
        if not task.question:
            return {
                "sql": "",
                "reasoning": "error=missing question",
                "task_id": task.task_id,
            }

        schema = normalize_schema(task.schema)
        candidates = plan_candidates(task, schema)
        if not candidates or candidates[0].confidence < 0.5:
            llm_sql = self.llm.generate(task, schema)
            if llm_sql:
                candidates.append(Candidate(sql=llm_sql, strategy="llm_fallback", confidence=0.7))

        ranked = []
        for candidate in candidates:
            report = validate_sql(candidate.sql, schema, dialect=task.dialect)
            penalty = 0.5 if report.errors else 0.0
            ranked.append((candidate.confidence - penalty, candidate, report))

        ranked.sort(key=lambda item: item[0], reverse=True)
        _, chosen, report = ranked[0]
        validation = "ok" if report.ok else ",".join(report.errors)

        return {
            "sql": chosen.sql,
            "reasoning": f"strategy={chosen.strategy}; validation={validation}",
            "task_id": task.task_id,
        }
