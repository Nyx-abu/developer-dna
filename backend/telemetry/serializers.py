"""
DRF serializers for all telemetry models.

Design notes:
 - UserSerializer is read-only and never exposes the password hash.
 - CodingSessionSerializer includes annotated event counts so the frontend
   can render session cards without N+1 queries.
 - EventIngestSerializer accepts a heterogeneous list of events for the
   batch ingest endpoint — the IDE plugin fires one POST per flush cycle.
"""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from telemetry.models import (
    AIInsight,
    CodeEvent,
    CodingSession,
    ErrorEvent,
    GitEvent,
    SkillSnapshot,
    TerminalEvent,
    User,
    WeeklyReport,
)


# ──────────────────────────────────────────────────────────────────────────────
# User
# ──────────────────────────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    """Read-only representation — password is never serialised."""

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "api_key",
            "timezone",
            "created_at",
        )
        read_only_fields = fields


# ──────────────────────────────────────────────────────────────────────────────
# CodingSession
# ──────────────────────────────────────────────────────────────────────────────

class CodingSessionSerializer(serializers.ModelSerializer):
    """
    Includes aggregated event counts so the frontend can show a session
    summary without extra API calls.  Counts are injected via annotation
    in the viewset queryset.
    """

    code_event_count: serializers.IntegerField = serializers.IntegerField(
        read_only=True, default=0,
    )
    git_event_count: serializers.IntegerField = serializers.IntegerField(
        read_only=True, default=0,
    )
    terminal_event_count: serializers.IntegerField = serializers.IntegerField(
        read_only=True, default=0,
    )
    error_event_count: serializers.IntegerField = serializers.IntegerField(
        read_only=True, default=0,
    )

    class Meta:
        model = CodingSession
        fields = (
            "id",
            "user",
            "start_time",
            "end_time",
            "duration_seconds",
            "editor",
            "is_active",
            "code_event_count",
            "git_event_count",
            "terminal_event_count",
            "error_event_count",
        )


# ──────────────────────────────────────────────────────────────────────────────
# Event serializers (one per event type)
# ──────────────────────────────────────────────────────────────────────────────

class CodeEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeEvent
        fields = (
            "id",
            "session",
            "event_type",
            "file_path",
            "language",
            "line_count",
            "char_count",
            "timestamp",
        )


class GitEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = GitEvent
        fields = (
            "id",
            "session",
            "event_type",
            "branch",
            "files_changed",
            "insertions",
            "deletions",
            "commit_hash",
            "message",
            "timestamp",
        )


class TerminalEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TerminalEvent
        fields = (
            "id",
            "session",
            "command",
            "exit_code",
            "duration_ms",
            "shell",
            "timestamp",
        )


class ErrorEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorEvent
        fields = (
            "id",
            "session",
            "error_type",
            "message",
            "file_path",
            "language",
            "line_number",
            "source",
            "severity",
            "resolved",
            "resolution_time_seconds",
            "timestamp",
        )


# ──────────────────────────────────────────────────────────────────────────────
# Insight / Report serializers
# ──────────────────────────────────────────────────────────────────────────────

class SkillSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillSnapshot
        fields = (
            "id",
            "user",
            "language",
            "framework",
            "proficiency_score",
            "evidence",
            "period",
            "created_at",
        )


class AIInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIInsight
        fields = (
            "id",
            "user",
            "insight_type",
            "title",
            "body",
            "severity",
            "actionable",
            "metadata",
            "created_at",
        )


class WeeklyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyReport
        fields = (
            "id",
            "user",
            "week_start",
            "week_end",
            "report_data",
            "summary",
            "created_at",
        )


# ──────────────────────────────────────────────────────────────────────────────
# Batch ingest
# ──────────────────────────────────────────────────────────────────────────────

class SingleEventSerializer(serializers.Serializer):
    """
    Schema for one event inside the batch ingest payload.

    The IDE plugin sends a flat `event_type` discriminator so we know
    which Kafka topic to route to; all remaining fields ride in `data`.
    """

    event_type = serializers.ChoiceField(
        choices=[
            "code_event",
            "git_event",
            "terminal_event",
            "error_event",
            "session_event",
        ],
    )
    data = serializers.DictField(
        help_text="Event payload — shape depends on event_type.",
    )

    def validate_data(self, value: dict[str, Any]) -> dict[str, Any]:
        """Ensure the payload is not empty."""
        if not value:
            raise serializers.ValidationError("Event data must not be empty.")
        return value


class EventIngestSerializer(serializers.Serializer):
    """
    Top-level ingest payload: a list of heterogeneous events.

    Example body::

        {
            "events": [
                {"event_type": "code_event", "data": {...}},
                {"event_type": "git_event",  "data": {...}}
            ]
        }
    """

    events = serializers.ListField(
        child=SingleEventSerializer(),
        allow_empty=False,
        help_text="One or more events to ingest in a single batch.",
    )
