import logging
from typing import Any

from django.db import transaction

logger = logging.getLogger(__name__)


def handle_code_event(data: dict[str, Any]) -> None:
    from telemetry.models import CodeEvent, CodingSession
    session_id = data.get("session_id")
    if not session_id:
        return
    try:
        session = CodingSession.objects.get(id=session_id)
        CodeEvent.objects.create(
            session=session,
            event_type=data.get("event_type"),
            file_path=data.get("file_path", ""),
            language=data.get("language", ""),
            line_count=data.get("line_count", 0),
            char_count=data.get("char_count", 0),
            timestamp=data.get("timestamp")
        )
    except CodingSession.DoesNotExist:
        logger.warning(f"Session {session_id} not found for code event.")


def handle_git_event(data: dict[str, Any]) -> None:
    from telemetry.models import GitEvent, CodingSession
    session_id = data.get("session_id")
    if not session_id:
        return
    try:
        session = CodingSession.objects.get(id=session_id)
        GitEvent.objects.create(
            session=session,
            event_type=data.get("event_type"),
            branch=data.get("branch", ""),
            files_changed=data.get("files_changed", 0),
            insertions=data.get("insertions", 0),
            deletions=data.get("deletions", 0),
            commit_hash=data.get("commit_hash", ""),
            message=data.get("message", ""),
            timestamp=data.get("timestamp")
        )
    except CodingSession.DoesNotExist:
        logger.warning(f"Session {session_id} not found for git event.")


def handle_terminal_event(data: dict[str, Any]) -> None:
    from telemetry.models import TerminalEvent, CodingSession
    session_id = data.get("session_id")
    if not session_id:
        return
    try:
        session = CodingSession.objects.get(id=session_id)
        TerminalEvent.objects.create(
            session=session,
            command=data.get("command", ""),
            exit_code=data.get("exit_code"),
            duration_ms=data.get("duration_ms"),
            shell=data.get("shell", ""),
            timestamp=data.get("timestamp")
        )
    except CodingSession.DoesNotExist:
        logger.warning(f"Session {session_id} not found for terminal event.")


def handle_error_event(data: dict[str, Any]) -> None:
    from telemetry.models import ErrorEvent, CodingSession
    session_id = data.get("session_id")
    if not session_id:
        return
    try:
        session = CodingSession.objects.get(id=session_id)
        ErrorEvent.objects.create(
            session=session,
            error_type=data.get("error_type", ""),
            message=data.get("message", ""),
            file_path=data.get("file_path", ""),
            language=data.get("language", ""),
            line_number=data.get("line_number"),
            source=data.get("source", ""),
            severity=data.get("severity", "error"),
            timestamp=data.get("timestamp")
        )
    except CodingSession.DoesNotExist:
        logger.warning(f"Session {session_id} not found for error event.")


def handle_session_event(data: dict[str, Any]) -> None:
    from telemetry.models import CodingSession
    user_id = data.get("user_id")
    if not user_id:
        return
    event_type = data.get("event_type")
    
    if event_type == "session_start":
        CodingSession.objects.create(
            user_id=user_id,
            start_time=data.get("timestamp"),
            end_time=data.get("timestamp"),  # will update on end
            editor=data.get("editor", "vscode"),
            is_active=True
        )
    elif event_type == "session_end":
        session_id = data.get("session_id")
        if session_id:
            try:
                session = CodingSession.objects.get(id=session_id)
                session.is_active = False
                session.end_time = data.get("timestamp")
                session.duration_seconds = data.get("duration_seconds", 0)
                session.save()
            except CodingSession.DoesNotExist:
                pass


def handle_analysis_request(data: dict[str, Any]) -> None:
    from agents.graph.workflow import run_analysis
    user_id = data.get("user_id")
    period_start = data.get("period_start")
    period_end = data.get("period_end")
    if user_id and period_start and period_end:
        run_analysis(user_id, period_start, period_end)


def handle_skill_insight(data: dict[str, Any]) -> None:
    from telemetry.models import SkillSnapshot
    user_id = data.get("user_id")
    if not user_id:
        return
    SkillSnapshot.objects.create(
        user_id=user_id,
        language=data.get("language", ""),
        framework=data.get("framework"),
        proficiency_score=data.get("proficiency_score", 0),
        evidence=data.get("evidence", {}),
        period=data.get("period", "")
    )


def handle_weekly_report(data: dict[str, Any]) -> None:
    from telemetry.models import WeeklyReport
    user_id = data.get("user_id")
    if not user_id:
        return
    WeeklyReport.objects.create(
        user_id=user_id,
        week_start=data.get("week_start"),
        week_end=data.get("week_end"),
        report_data=data.get("report_data", {}),
        summary=data.get("summary", "")
    )


def handle_anomaly_event(data: dict[str, Any]) -> None:
    from telemetry.models import AIInsight
    user_id = data.get("user_id")
    if not user_id:
        return
    AIInsight.objects.create(
        user_id=user_id,
        insight_type="anomaly",
        title=data.get("title", ""),
        body=data.get("body", ""),
        severity=data.get("severity", "info"),
        actionable=data.get("actionable", False),
        metadata=data.get("metadata", {})
    )


EVENT_HANDLERS = {
    "code-events": handle_code_event,
    "git-events": handle_git_event,
    "terminal-events": handle_terminal_event,
    "error-events": handle_error_event,
    "session-events": handle_session_event,
    "analysis-requests": handle_analysis_request,
    "skill-insights": handle_skill_insight,
    "weekly-reports": handle_weekly_report,
    "anomaly-events": handle_anomaly_event,
}

def route_message(topic: str, data: dict[str, Any]) -> None:
    handler = EVENT_HANDLERS.get(topic)
    if handler:
        try:
            with transaction.atomic():
                handler(data)
        except Exception as e:
            logger.error(f"Error handling event for topic {topic}: {e}")
            raise e
    else:
        logger.warning(f"No handler for topic {topic}")
