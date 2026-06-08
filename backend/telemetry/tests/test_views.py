import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from telemetry.models import CodingSession
from unittest.mock import patch

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
@patch("events.kafka_producer.KafkaProducer.publish_event")
def test_ingest_events(mock_publish, api_client, test_user):
    url = reverse('ingest')
    payload = {
        "events": [
            {
                "event_id": "123e4567-e89b-12d3-a456-426614174000",
                "event_type": "file_save",
                "timestamp": "2024-01-01T10:00:00Z",
                "file_path": "main.py",
                "language": "python",
                "line_count": 100,
                "char_count": 2500
            }
        ]
    }
    
    # Needs auth
    api_client.force_authenticate(user=test_user)
    response = api_client.post(url, payload, format='json')
    
    assert response.status_code == 201
    assert mock_publish.called

@pytest.mark.django_db
def test_get_sessions(api_client, test_session):
    url = reverse('session-list')
    api_client.force_authenticate(user=test_session.user)
    response = api_client.get(url)
    
    assert response.status_code == 200
    assert len(response.data) > 0
    assert response.data[0]['id'] == test_session.id
