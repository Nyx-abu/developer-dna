"""
DRF views for the Developer DNA telemetry API.

Design decisions:
 - EventIngestView validates with Pydantic (for speed + strict typing)
   then publishes each event to its Kafka topic.  The DB write happens
   asynchronously via the consumer, keeping ingest latency low.
 - All read ViewSets use simple query-param filtering instead of
   django-filter to keep dependencies lean.
 - Every error response follows the {error, code, detail} contract
   so the frontend can render consistent error UIs.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from django.db.models import Count, QuerySet
from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from events.kafka_producer import publish_event
from events.schemas import (
    AnalysisRequestSchema,
    CodeEventSchema,
    ErrorEventSchema,
    GitEventSchema,
    SessionEventSchema,
    TerminalEventSchema,
)
from telemetry.models import (
    AIInsight,
    CodeEvent,
    CodingSession,
    ErrorEvent,
    GitEvent,
    SkillSnapshot,
    TerminalEvent,
    WeeklyReport,
)
from telemetry.serializers import (
    AIInsightSerializer,
    CodeEventSerializer,
    CodingSessionSerializer,
    ErrorEventSerializer,
    EventIngestSerializer,
    GitEventSerializer,
    SkillSnapshotSerializer,
    TerminalEventSerializer,
    WeeklyReportSerializer,
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _error_response(
    error: str,
    code: str,
    detail: str,
    http_status: int = status.HTTP_400_BAD_REQUEST,
) -> Response:
    """Standardised error envelope used by every endpoint."""
    return Response(
        {"error": error, "code": code, "detail": detail},
        status=http_status,
    )


# Mapping from the ingest payload's event_type discriminator to a
# (Pydantic schema, Kafka topic) pair.
_EVENT_ROUTING: dict[str, tuple[type, str]] = {
    "code_event": (CodeEventSchema, "code-events"),
    "git_event": (GitEventSchema, "git-events"),
    "terminal_event": (TerminalEventSchema, "terminal-events"),
    "error_event": (ErrorEventSchema, "error-events"),
    "session_event": (SessionEventSchema, "session-events"),
}


# ──────────────────────────────────────────────────────────────────────────────
# EventIngestView — POST /api/v1/events/ingest/
# ──────────────────────────────────────────────────────────────────────────────

class EventIngestView(APIView):
    """
    Accepts a batch of heterogeneous events from the IDE plugin, validates
    each with its Pydantic schema, and publishes to the appropriate Kafka
    topic.  Returns 201 on success.

    The actual DB persistence is done by the Kafka consumer so that the
    ingest path stays fast even under heavy load.
    """

    def post(self, request: Request) -> Response:
        drf_serializer = EventIngestSerializer(data=request.data)
        if not drf_serializer.is_valid():
            return _error_response(
                error="Validation failed",
                code="INVALID_PAYLOAD",
                detail=str(drf_serializer.errors),
            )

        events: list[dict[str, Any]] = drf_serializer.validated_data["events"]
        published = 0
        errors: list[dict[str, str]] = []

        for idx, event_envelope in enumerate(events):
            event_type: str = event_envelope["event_type"]
            data: dict[str, Any] = event_envelope["data"]

            route = _EVENT_ROUTING.get(event_type)
            if route is None:
                errors.append({
                    "index": str(idx),
                    "error": f"Unknown event_type '{event_type}'",
                })
                continue

            schema_cls, topic = route

            try:
                # Pydantic v2 strict validation
                validated = schema_cls.model_validate(data)
            except Exception as exc:
                errors.append({
                    "index": str(idx),
                    "error": str(exc),
                })
                continue

            # Key by user_id so all events for a user land in the same
            # partition, preserving per-user ordering.
            key = str(validated.user_id) if validated.user_id else "anonymous"
            publish_event(topic=topic, key=key, event_schema=validated)
            published += 1

        response_status = (
            status.HTTP_201_CREATED if published > 0
            else status.HTTP_400_BAD_REQUEST
        )
        return Response(
            {
                "published": published,
                "errors": errors,
            },
            status=response_status,
        )


# ──────────────────────────────────────────────────────────────────────────────
# AnalysisTriggerView — POST /api/v1/analysis/trigger/
# ──────────────────────────────────────────────────────────────────────────────

class AnalysisTriggerView(APIView):
    """
    Enqueues an analysis-request on Kafka.  The LangGraph consumer
    picks it up and runs the full agent pipeline.
    """

    def post(self, request: Request) -> Response:
        try:
            payload = AnalysisRequestSchema.model_validate(request.data)
        except Exception as exc:
            return _error_response(
                error="Validation failed",
                code="INVALID_ANALYSIS_REQUEST",
                detail=str(exc),
            )

        publish_event(
            topic="analysis-requests",
            key=str(payload.user_id),
            event_schema=payload,
        )

        return Response(
            {"status": "queued", "user_id": payload.user_id},
            status=status.HTTP_201_CREATED,
        )


# ──────────────────────────────────────────────────────────────────────────────
# Read-only ViewSets
# ──────────────────────────────────────────────────────────────────────────────

class CodingSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """List / retrieve coding sessions, optionally filtered by user."""

    serializer_class = CodingSessionSerializer

    def get_queryset(self) -> QuerySet[CodingSession]:
        qs = (
            CodingSession.objects
            .select_related("user")
            .annotate(
                code_event_count=Count("code_events"),
                git_event_count=Count("git_events"),
                terminal_event_count=Count("terminal_events"),
                error_event_count=Count("error_events"),
            )
        )
        user_id = self.request.query_params.get("user_id")
        if user_id is not None:
            qs = qs.filter(user_id=user_id)
        return qs


class _EventViewSetBase(viewsets.ReadOnlyModelViewSet):
    """
    Shared base for the four event viewsets — provides session and date
    filtering so we don't repeat ourselves.
    """

    def _apply_common_filters(self, qs: QuerySet) -> QuerySet:  # type: ignore[type-arg]
        session_id = self.request.query_params.get("session_id")
        if session_id is not None:
            qs = qs.filter(session_id=session_id)

        date_from = self.request.query_params.get("date_from")
        if date_from is not None:
            qs = qs.filter(timestamp__gte=datetime.fromisoformat(date_from))

        date_to = self.request.query_params.get("date_to")
        if date_to is not None:
            qs = qs.filter(timestamp__lte=datetime.fromisoformat(date_to))

        return qs


class CodeEventViewSet(_EventViewSetBase):
    serializer_class = CodeEventSerializer

    def get_queryset(self) -> QuerySet[CodeEvent]:
        return self._apply_common_filters(CodeEvent.objects.all())


class GitEventViewSet(_EventViewSetBase):
    serializer_class = GitEventSerializer

    def get_queryset(self) -> QuerySet[GitEvent]:
        return self._apply_common_filters(GitEvent.objects.all())


class TerminalEventViewSet(_EventViewSetBase):
    serializer_class = TerminalEventSerializer

    def get_queryset(self) -> QuerySet[TerminalEvent]:
        return self._apply_common_filters(TerminalEvent.objects.all())


class ErrorEventViewSet(_EventViewSetBase):
    serializer_class = ErrorEventSerializer

    def get_queryset(self) -> QuerySet[ErrorEvent]:
        return self._apply_common_filters(ErrorEvent.objects.all())


class SkillSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SkillSnapshotSerializer

    def get_queryset(self) -> QuerySet[SkillSnapshot]:
        qs = SkillSnapshot.objects.all()
        user_id = self.request.query_params.get("user_id")
        if user_id is not None:
            qs = qs.filter(user_id=user_id)
        language = self.request.query_params.get("language")
        if language is not None:
            qs = qs.filter(language__iexact=language)
        return qs


class AIInsightViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AIInsightSerializer

    def get_queryset(self) -> QuerySet[AIInsight]:
        qs = AIInsight.objects.all()
        user_id = self.request.query_params.get("user_id")
        if user_id is not None:
            qs = qs.filter(user_id=user_id)
        insight_type = self.request.query_params.get("type")
        if insight_type is not None:
            qs = qs.filter(insight_type=insight_type)
        return qs


class WeeklyReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WeeklyReportSerializer

    def get_queryset(self) -> QuerySet[WeeklyReport]:
        qs = WeeklyReport.objects.all()
        user_id = self.request.query_params.get("user_id")
        if user_id is not None:
            qs = qs.filter(user_id=user_id)
        return qs
