"""
Pydantic v2 schemas for every Kafka message type.

Why Pydantic instead of DRF serializers for Kafka?
 - Pydantic is ~4× faster for pure validation
 - We want model_dump(mode="json") for confluent-kafka's value serialiser
 - Type-safe defaults (uuid4, datetime.now) are cleaner in Pydantic
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────────────────────────────────────
# Base
# ──────────────────────────────────────────────────────────────────────────────

class BaseEvent(BaseModel):
    """Fields every event carries."""

    event_id: UUID = Field(default_factory=uuid4)
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[int] = None


# ──────────────────────────────────────────────────────────────────────────────
# Code events
# ──────────────────────────────────────────────────────────────────────────────

class CodeEventSchema(BaseEvent):
    event_type: Literal["file_save", "file_open", "file_close", "keystroke_batch"]
    file_path: str
    language: str = "unknown"
    line_count: int = 0
    char_count: int = 0


# ──────────────────────────────────────────────────────────────────────────────
# Git events
# ──────────────────────────────────────────────────────────────────────────────

class GitEventSchema(BaseEvent):
    event_type: Literal["commit", "push", "pull", "branch_switch", "merge"]
    branch: str = ""
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0
    commit_hash: str = ""
    message: str = ""


# ──────────────────────────────────────────────────────────────────────────────
# Terminal events
# ──────────────────────────────────────────────────────────────────────────────

class TerminalEventSchema(BaseEvent):
    event_type: Literal["terminal_command"] = "terminal_command"
    command: str
    exit_code: int = 0
    duration_ms: int = 0
    shell: str = "unknown"


# ──────────────────────────────────────────────────────────────────────────────
# Error events
# ──────────────────────────────────────────────────────────────────────────────

class ErrorEventSchema(BaseEvent):
    event_type: Literal["error"] = "error"
    error_type: str
    message: str
    file_path: str = ""
    language: str = "unknown"
    line_number: Optional[int] = None
    source: str = "unknown"
    severity: Literal["info", "warning", "error", "critical"] = "error"


# ──────────────────────────────────────────────────────────────────────────────
# Session lifecycle events
# ──────────────────────────────────────────────────────────────────────────────

class SessionEventSchema(BaseEvent):
    event_type: Literal["session_start", "session_end"]
    session_type: Literal["start", "end"]
    editor: str = "unknown"
    duration_seconds: Optional[int] = None


# ──────────────────────────────────────────────────────────────────────────────
# Analysis requests (not a telemetry event, but uses the same transport)
# ──────────────────────────────────────────────────────────────────────────────

class AnalysisRequestSchema(BaseModel):
    """Payload published to the analysis-requests topic."""

    user_id: int
    period_start: datetime
    period_end: datetime
    request_type: Literal[
        "full",
        "skill_only",
        "productivity_only",
        "debug_only",
    ] = "full"
