"""
Telemetry models — the canonical data layer for Developer DNA.

Every model carries composite indexes tuned for the two dominant access
patterns: "give me everything for a user" and "give me everything for a
session in chronological order".
"""

from __future__ import annotations

import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone as django_timezone


# ──────────────────────────────────────────────────────────────────────────────
# User
# ──────────────────────────────────────────────────────────────────────────────

class User(AbstractUser):
    """
    Extended user with an auto-generated API key for IDE plugin auth
    and a timezone so we can localise insights.
    """

    api_key: models.UUIDField = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text="Auto-generated key the IDE plugin sends in X-API-Key header.",
    )
    timezone: models.CharField = models.CharField(
        max_length=64,
        default="UTC",
        help_text="IANA timezone, e.g. 'Asia/Kolkata'.",
    )
    created_at: models.DateTimeField = models.DateTimeField(
        default=django_timezone.now,
        help_text="When this account was provisioned.",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self) -> str:
        return f"{self.username} ({self.email})"


# ──────────────────────────────────────────────────────────────────────────────
# CodingSession
# ──────────────────────────────────────────────────────────────────────────────

class CodingSession(models.Model):
    """
    A contiguous window of editor activity.  The IDE plugin opens a session
    on focus-in and closes it on focus-out / idle timeout.
    """

    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    start_time: models.DateTimeField = models.DateTimeField(default=django_timezone.now)
    end_time: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    duration_seconds: models.PositiveIntegerField = models.PositiveIntegerField(
        default=0,
        help_text="Computed on session close or periodically while active.",
    )
    editor: models.CharField = models.CharField(
        max_length=64,
        default="unknown",
        help_text="Editor identifier, e.g. 'vscode', 'neovim'.",
    )
    is_active: models.BooleanField = models.BooleanField(
        default=True,
        help_text="Flipped to False when the session closes.",
    )

    class Meta:
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["user", "start_time"], name="idx_session_user_start"),
        ]

    def __str__(self) -> str:
        status = "active" if self.is_active else "closed"
        return f"Session {self.pk} [{status}] — {self.user}"


# ──────────────────────────────────────────────────────────────────────────────
# CodeEvent
# ──────────────────────────────────────────────────────────────────────────────

class CodeEvent(models.Model):
    """
    Individual code-level events fired by the IDE plugin:
    saves, opens, closes, and periodic keystroke-batch snapshots.
    """

    class EventType(models.TextChoices):
        FILE_SAVE = "file_save", "File Save"
        FILE_OPEN = "file_open", "File Open"
        FILE_CLOSE = "file_close", "File Close"
        KEYSTROKE_BATCH = "keystroke_batch", "Keystroke Batch"

    session: models.ForeignKey = models.ForeignKey(
        CodingSession,
        on_delete=models.CASCADE,
        related_name="code_events",
    )
    event_type: models.CharField = models.CharField(
        max_length=32,
        choices=EventType.choices,
    )
    file_path: models.CharField = models.CharField(max_length=512)
    language: models.CharField = models.CharField(
        max_length=64,
        default="unknown",
        help_text="Detected programming language of the file.",
    )
    line_count: models.PositiveIntegerField = models.PositiveIntegerField(default=0)
    char_count: models.PositiveIntegerField = models.PositiveIntegerField(default=0)
    timestamp: models.DateTimeField = models.DateTimeField(default=django_timezone.now)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["session", "timestamp"], name="idx_code_session_ts"),
            models.Index(fields=["language"], name="idx_code_language"),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} — {self.file_path}"


# ──────────────────────────────────────────────────────────────────────────────
# GitEvent
# ──────────────────────────────────────────────────────────────────────────────

class GitEvent(models.Model):
    """Git operations captured by the IDE plugin or a local Git hook."""

    class EventType(models.TextChoices):
        COMMIT = "commit", "Commit"
        PUSH = "push", "Push"
        PULL = "pull", "Pull"
        BRANCH_SWITCH = "branch_switch", "Branch Switch"
        MERGE = "merge", "Merge"

    session: models.ForeignKey = models.ForeignKey(
        CodingSession,
        on_delete=models.CASCADE,
        related_name="git_events",
    )
    event_type: models.CharField = models.CharField(
        max_length=32,
        choices=EventType.choices,
    )
    branch: models.CharField = models.CharField(max_length=255, default="")
    files_changed: models.PositiveIntegerField = models.PositiveIntegerField(default=0)
    insertions: models.PositiveIntegerField = models.PositiveIntegerField(default=0)
    deletions: models.PositiveIntegerField = models.PositiveIntegerField(default=0)
    commit_hash: models.CharField = models.CharField(max_length=64, blank=True, default="")
    message: models.TextField = models.TextField(blank=True, default="")
    timestamp: models.DateTimeField = models.DateTimeField(default=django_timezone.now)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["session", "timestamp"], name="idx_git_session_ts"),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} on {self.branch}"


# ──────────────────────────────────────────────────────────────────────────────
# TerminalEvent
# ──────────────────────────────────────────────────────────────────────────────

class TerminalEvent(models.Model):
    """Shell commands executed inside the editor's integrated terminal."""

    session: models.ForeignKey = models.ForeignKey(
        CodingSession,
        on_delete=models.CASCADE,
        related_name="terminal_events",
    )
    command: models.CharField = models.CharField(max_length=1024)
    exit_code: models.IntegerField = models.IntegerField(default=0)
    duration_ms: models.PositiveIntegerField = models.PositiveIntegerField(
        default=0,
        help_text="How long the command took to execute in milliseconds.",
    )
    shell: models.CharField = models.CharField(
        max_length=64,
        default="unknown",
        help_text="Shell type, e.g. 'bash', 'zsh', 'powershell'.",
    )
    timestamp: models.DateTimeField = models.DateTimeField(default=django_timezone.now)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["session", "timestamp"], name="idx_term_session_ts"),
        ]

    def __str__(self) -> str:
        return f"$ {self.command[:60]}"


# ──────────────────────────────────────────────────────────────────────────────
# ErrorEvent
# ──────────────────────────────────────────────────────────────────────────────

class ErrorEvent(models.Model):
    """
    Compiler errors, linter warnings, and runtime exceptions captured from
    the editor diagnostics API or terminal output.
    """

    class Severity(models.TextChoices):
        INFO = "info", "Info"
        WARNING = "warning", "Warning"
        ERROR = "error", "Error"
        CRITICAL = "critical", "Critical"

    session: models.ForeignKey = models.ForeignKey(
        CodingSession,
        on_delete=models.CASCADE,
        related_name="error_events",
    )
    error_type: models.CharField = models.CharField(max_length=128)
    message: models.TextField = models.TextField()
    file_path: models.CharField = models.CharField(max_length=512, blank=True, default="")
    language: models.CharField = models.CharField(max_length=64, default="unknown")
    line_number: models.PositiveIntegerField = models.PositiveIntegerField(
        null=True, blank=True,
    )
    source: models.CharField = models.CharField(
        max_length=64,
        default="unknown",
        help_text="Where the error came from: 'linter', 'compiler', 'runtime', etc.",
    )
    severity: models.CharField = models.CharField(
        max_length=16,
        choices=Severity.choices,
        default=Severity.ERROR,
    )
    resolved: models.BooleanField = models.BooleanField(
        default=False,
        help_text="Marked True when the error no longer appears in diagnostics.",
    )
    resolution_time_seconds: models.PositiveIntegerField = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Seconds between the error appearing and being resolved.",
    )
    timestamp: models.DateTimeField = models.DateTimeField(default=django_timezone.now)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["session", "timestamp"], name="idx_err_session_ts"),
            models.Index(fields=["resolved"], name="idx_err_resolved"),
        ]

    def __str__(self) -> str:
        return f"[{self.severity}] {self.error_type}: {self.message[:60]}"


# ──────────────────────────────────────────────────────────────────────────────
# SkillSnapshot
# ──────────────────────────────────────────────────────────────────────────────

class SkillSnapshot(models.Model):
    """
    A point-in-time proficiency assessment for a (user, language, period)
    triple.  Generated by the skill-analysis LangGraph agent.
    """

    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="skill_snapshots",
    )
    language: models.CharField = models.CharField(max_length=64)
    framework: models.CharField = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="Optional framework, e.g. 'Django', 'React'.",
    )
    proficiency_score: models.FloatField = models.FloatField(
        help_text="0–100 proficiency score produced by the LLM agent.",
    )
    evidence: models.JSONField = models.JSONField(
        default=dict,
        help_text="Supporting data the agent used to derive the score.",
    )
    period: models.CharField = models.CharField(
        max_length=16,
        help_text="ISO week like '2024-W01' or month like '2024-01'.",
    )
    created_at: models.DateTimeField = models.DateTimeField(default=django_timezone.now)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("user", "language", "period")]

    def __str__(self) -> str:
        return f"{self.user} — {self.language} @ {self.proficiency_score:.0f} ({self.period})"


# ──────────────────────────────────────────────────────────────────────────────
# AIInsight
# ──────────────────────────────────────────────────────────────────────────────

class AIInsight(models.Model):
    """
    A discrete insight generated by one of the LangGraph agents.
    Think of it as a notification card in the dashboard.
    """

    class InsightType(models.TextChoices):
        SKILL = "skill", "Skill"
        PRODUCTIVITY = "productivity", "Productivity"
        DEBUG = "debug", "Debug"
        CAREER = "career", "Career"
        ANOMALY = "anomaly", "Anomaly"

    class Severity(models.TextChoices):
        INFO = "info", "Info"
        WARNING = "warning", "Warning"
        CRITICAL = "critical", "Critical"

    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="insights",
    )
    insight_type: models.CharField = models.CharField(
        max_length=32,
        choices=InsightType.choices,
    )
    title: models.CharField = models.CharField(max_length=255)
    body: models.TextField = models.TextField()
    severity: models.CharField = models.CharField(
        max_length=16,
        choices=Severity.choices,
        default=Severity.INFO,
    )
    actionable: models.BooleanField = models.BooleanField(
        default=False,
        help_text="True if the insight contains a concrete action the dev can take.",
    )
    metadata: models.JSONField = models.JSONField(
        default=dict,
        help_text="Freeform data the agent attaches for the frontend to render.",
    )
    created_at: models.DateTimeField = models.DateTimeField(default=django_timezone.now)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["user", "insight_type", "created_at"],
                name="idx_insight_user_type_ts",
            ),
        ]

    def __str__(self) -> str:
        return f"[{self.insight_type}] {self.title}"


# ──────────────────────────────────────────────────────────────────────────────
# WeeklyReport
# ──────────────────────────────────────────────────────────────────────────────

class WeeklyReport(models.Model):
    """
    Spotify-Wrapped-style weekly developer report produced by the
    report agent at the end of each ISO week.
    """

    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="weekly_reports",
    )
    week_start: models.DateField = models.DateField()
    week_end: models.DateField = models.DateField()
    report_data: models.JSONField = models.JSONField(
        default=dict,
        help_text="Full structured report (highlights, badges, tips, etc.).",
    )
    summary: models.TextField = models.TextField(
        blank=True,
        default="",
        help_text="Human-readable narrative summary.",
    )
    created_at: models.DateTimeField = models.DateTimeField(default=django_timezone.now)

    class Meta:
        ordering = ["-week_start"]
        unique_together = [("user", "week_start")]

    def __str__(self) -> str:
        return f"Report {self.week_start} → {self.week_end} — {self.user}"
