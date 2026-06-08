"""
URL routing for the telemetry API (mounted at /api/v1/).

Uses DRF's DefaultRouter for standard CRUD viewsets and explicit paths
for the two action endpoints (ingest + analysis trigger).
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from telemetry.views import (
    AIInsightViewSet,
    AnalysisTriggerView,
    CodeEventViewSet,
    CodingSessionViewSet,
    ErrorEventViewSet,
    EventIngestView,
    GitEventViewSet,
    SkillSnapshotViewSet,
    TerminalEventViewSet,
    WeeklyReportViewSet,
)

router = DefaultRouter()
router.register(r"sessions", CodingSessionViewSet, basename="session")
router.register(r"code-events", CodeEventViewSet, basename="code-event")
router.register(r"git-events", GitEventViewSet, basename="git-event")
router.register(r"terminal-events", TerminalEventViewSet, basename="terminal-event")
router.register(r"error-events", ErrorEventViewSet, basename="error-event")
router.register(r"skills", SkillSnapshotViewSet, basename="skill")
router.register(r"insights", AIInsightViewSet, basename="insight")
router.register(r"reports", WeeklyReportViewSet, basename="report")

urlpatterns = [
    # Action endpoints
    path("events/ingest/", EventIngestView.as_view(), name="event-ingest"),
    path("analysis/trigger/", AnalysisTriggerView.as_view(), name="analysis-trigger"),
    # Router-generated CRUD routes
    path("", include(router.urls)),
]
