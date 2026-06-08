"""
Admin registrations for all telemetry models.

Every model gets list_display (for the table view), list_filter (sidebar
facets), and search_fields (top search bar) tuned for operational debugging.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

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

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Extends the stock UserAdmin with our extra fields."""

    list_display = ("username", "email", "api_key", "timezone", "created_at", "is_active")
    list_filter = ("is_active", "is_staff", "timezone")
    search_fields = ("username", "email", "api_key")
    readonly_fields = ("api_key", "created_at")

    # Inject our fields into the "Personal info" fieldset
    fieldsets = BaseUserAdmin.fieldsets + (  # type: ignore[operator]
        ("Developer DNA", {"fields": ("api_key", "timezone", "created_at")}),
    )


# ──────────────────────────────────────────────────────────────────────────────
# CodingSession
# ──────────────────────────────────────────────────────────────────────────────

@admin.register(CodingSession)
class CodingSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "start_time", "end_time", "duration_seconds", "editor", "is_active")
    list_filter = ("is_active", "editor")
    search_fields = ("user__username",)
    raw_id_fields = ("user",)


# ──────────────────────────────────────────────────────────────────────────────
# CodeEvent
# ──────────────────────────────────────────────────────────────────────────────

@admin.register(CodeEvent)
class CodeEventAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "event_type", "file_path", "language", "line_count", "timestamp")
    list_filter = ("event_type", "language")
    search_fields = ("file_path", "language")
    raw_id_fields = ("session",)


# ──────────────────────────────────────────────────────────────────────────────
# GitEvent
# ──────────────────────────────────────────────────────────────────────────────

@admin.register(GitEvent)
class GitEventAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "event_type", "branch", "files_changed", "insertions", "deletions", "timestamp")
    list_filter = ("event_type",)
    search_fields = ("branch", "commit_hash", "message")
    raw_id_fields = ("session",)


# ──────────────────────────────────────────────────────────────────────────────
# TerminalEvent
# ──────────────────────────────────────────────────────────────────────────────

@admin.register(TerminalEvent)
class TerminalEventAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "command", "exit_code", "duration_ms", "shell", "timestamp")
    list_filter = ("shell", "exit_code")
    search_fields = ("command",)
    raw_id_fields = ("session",)


# ──────────────────────────────────────────────────────────────────────────────
# ErrorEvent
# ──────────────────────────────────────────────────────────────────────────────

@admin.register(ErrorEvent)
class ErrorEventAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "error_type", "severity", "resolved", "language", "timestamp")
    list_filter = ("severity", "resolved", "source", "language")
    search_fields = ("error_type", "message", "file_path")
    raw_id_fields = ("session",)


# ──────────────────────────────────────────────────────────────────────────────
# SkillSnapshot
# ──────────────────────────────────────────────────────────────────────────────

@admin.register(SkillSnapshot)
class SkillSnapshotAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "language", "framework", "proficiency_score", "period", "created_at")
    list_filter = ("language", "period")
    search_fields = ("user__username", "language", "framework")
    raw_id_fields = ("user",)


# ──────────────────────────────────────────────────────────────────────────────
# AIInsight
# ──────────────────────────────────────────────────────────────────────────────

@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "insight_type", "title", "severity", "actionable", "created_at")
    list_filter = ("insight_type", "severity", "actionable")
    search_fields = ("title", "body", "user__username")
    raw_id_fields = ("user",)


# ──────────────────────────────────────────────────────────────────────────────
# WeeklyReport
# ──────────────────────────────────────────────────────────────────────────────

@admin.register(WeeklyReport)
class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "week_start", "week_end", "created_at")
    list_filter = ("week_start",)
    search_fields = ("user__username", "summary")
    raw_id_fields = ("user",)
