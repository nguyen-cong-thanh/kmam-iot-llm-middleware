"""AuditLogger (FR5): record every allow/deny decision for traceability.

Records are kept in memory and, optionally, appended to a JSONL file so an experiment
run can be inspected and reproduced (report sections 2.2.3 and 3.2). The timestamp
source is injectable to keep tests deterministic.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from kmam.context import Decision, RequestContext


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AuditRecord:
    """A single audited decision."""

    timestamp: str
    session_id: str
    user_id: str | None
    role: str | None
    device_id: str | None
    action: str | None
    params: dict[str, Any]
    verdict: str
    stage: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AuditLogger:
    """Collects audit records, optionally persisting them to a JSONL sink."""

    def __init__(
        self,
        sink: str | Path | None = None,
        clock: Callable[[], str] = _utc_now,
    ) -> None:
        self.sink = Path(sink) if sink is not None else None
        self.clock = clock
        self.records: list[AuditRecord] = []
        if self.sink is not None:
            self.sink.parent.mkdir(parents=True, exist_ok=True)

    def log(self, ctx: RequestContext, decision: Decision) -> AuditRecord:
        record = AuditRecord(
            timestamp=self.clock(),
            session_id=ctx.session_id,
            user_id=ctx.user_id,
            role=ctx.role,
            device_id=ctx.device_id,
            action=ctx.action,
            params=dict(ctx.params),
            verdict=decision.verdict.value,
            stage=decision.stage,
            reason=decision.reason,
        )
        self.records.append(record)
        if self.sink is not None:
            with self.sink.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
        return record

    def clear(self) -> None:
        self.records.clear()
