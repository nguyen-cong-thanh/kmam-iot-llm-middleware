"""Tests for the AuditLogger (FR5)."""

import json

from kmam.audit import AuditLogger
from kmam.context import Decision, RequestContext


def _ctx():
    return RequestContext(
        session_id="token-admin-001",
        user_id="alice",
        role="admin",
        device_id="lock_front",
        action="unlock",
    )


def test_log_captures_request_and_decision():
    logger = AuditLogger(clock=lambda: "2026-01-01T00:00:00+00:00")
    record = logger.log(_ctx(), Decision.allow("access_control", "authorized"))
    assert record.user_id == "alice"
    assert record.device_id == "lock_front"
    assert record.verdict == "allow"
    assert record.stage == "access_control"
    assert record.timestamp == "2026-01-01T00:00:00+00:00"


def test_records_accumulate():
    logger = AuditLogger()
    logger.log(_ctx(), Decision.allow())
    logger.log(_ctx(), Decision.deny("command_validation", "bad param"))
    assert len(logger.records) == 2
    assert logger.records[1].verdict == "deny"


def test_sink_writes_jsonl(tmp_path):
    sink = tmp_path / "logs" / "audit.jsonl"
    logger = AuditLogger(sink=sink, clock=lambda: "t0")
    logger.log(_ctx(), Decision.deny("authentication", "invalid credential"))
    lines = sink.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["verdict"] == "deny"
    assert payload["stage"] == "authentication"


def test_clear_empties_records():
    logger = AuditLogger()
    logger.log(_ctx(), Decision.allow())
    logger.clear()
    assert logger.records == []
