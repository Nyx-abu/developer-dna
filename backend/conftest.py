"""
Shared pytest fixtures for Developer DNA backend tests.

Provides test user, test session, mock Kafka producer, and mock LLM
so unit tests never need external services.
"""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from django.test import RequestFactory
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    """DRF API test client."""
    return APIClient()


@pytest.fixture
def request_factory() -> RequestFactory:
    """Django request factory."""
    return RequestFactory()


@pytest.fixture
def test_user(db):
    """Create a test user with an API key."""
    from telemetry.models import User

    user = User.objects.create_user(
        username="testdev",
        email="test@developerdna.dev",
        password="testpass123",
        api_key=uuid.uuid4(),
        timezone="UTC",
    )
    return user


@pytest.fixture
def test_session(db, test_user):
    """Create a test coding session."""
    from telemetry.models import CodingSession

    now = datetime.now(timezone.utc)
    session = CodingSession.objects.create(
        user=test_user,
        start_time=now - timedelta(hours=2),
        end_time=now,
        duration_seconds=7200,
        editor="vscode",
        is_active=False,
    )
    return session


@pytest.fixture
def mock_kafka_producer():
    """Mock Kafka producer — prevents real Kafka connections in tests."""
    with patch("events.kafka_producer.get_producer") as mock:
        producer = MagicMock()
        mock.return_value = producer
        yield producer


@pytest.fixture
def mock_llm():
    """Mock LLM — prevents real API calls in agent tests."""
    with patch("agents.llm.get_llm") as mock:
        llm = MagicMock()
        # Default response mimics LLM JSON output
        llm.invoke.return_value = MagicMock(
            content='{"analysis": "mock analysis result", "score": 75}'
        )
        mock.return_value = llm
        yield llm


@pytest.fixture
def sample_code_events() -> list[dict]:
    """Sample code events for testing agent analysis."""
    now = datetime.now(timezone.utc)
    return [
        {
            "event_type": "file_save",
            "file_path": "app/models.py",
            "language": "python",
            "line_count": 150,
            "char_count": 4200,
            "timestamp": (now - timedelta(hours=i)).isoformat(),
        }
        for i in range(10)
    ] + [
        {
            "event_type": "file_save",
            "file_path": "src/components/Dashboard.tsx",
            "language": "typescriptreact",
            "line_count": 89,
            "char_count": 2800,
            "timestamp": (now - timedelta(hours=i, minutes=30)).isoformat(),
        }
        for i in range(5)
    ]


@pytest.fixture
def sample_error_events() -> list[dict]:
    """Sample error events for testing debug agent."""
    now = datetime.now(timezone.utc)
    return [
        {
            "error_type": "SyntaxError",
            "message": "unexpected indent",
            "file_path": "app/views.py",
            "language": "python",
            "line_number": 42,
            "source": "pylint",
            "severity": "error",
            "timestamp": (now - timedelta(hours=i)).isoformat(),
        }
        for i in range(3)
    ]
