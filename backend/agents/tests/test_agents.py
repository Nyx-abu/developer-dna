import pytest
from unittest.mock import patch, MagicMock
from agents.graph.state import AnalysisState
from agents.skill_agent import skill_agent
from agents.productivity_agent import productivity_agent

@pytest.fixture
def mock_llm_response():
    mock = MagicMock()
    mock.content = '{"languages": {"python": {"lines_written": 1500}}}'
    return mock

@patch("agents.skill_agent.get_llm")
def test_skill_agent(mock_get_llm, mock_llm_response):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = mock_llm_response
    mock_get_llm.return_value = mock_llm

    state = AnalysisState(
        user_id=1,
        period_start="2024-01-01",
        period_end="2024-01-07",
        code_events=[{"language": "python", "line_count": 10}],
        git_events=[],
        error_events=[],
        terminal_events=[],
        skill_analysis={},
        productivity_analysis={},
        debug_analysis={},
        career_analysis={},
        report={},
        errors=[]
    )

    result = skill_agent(state)
    assert "skill_analysis" in result
    assert "languages" in result["skill_analysis"]
    assert "python" in result["skill_analysis"]["languages"]

@patch("agents.productivity_agent.get_llm")
def test_productivity_agent(mock_get_llm):
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = '{"peak_hours": ["09:00"]}'
    mock_llm.invoke.return_value = mock_response
    mock_get_llm.return_value = mock_llm

    state = AnalysisState(
        user_id=1,
        period_start="2024-01-01",
        period_end="2024-01-07",
        code_events=[],
        git_events=[],
        error_events=[],
        terminal_events=[],
        skill_analysis={},
        productivity_analysis={},
        debug_analysis={},
        career_analysis={},
        report={},
        errors=[]
    )

    result = productivity_agent(state)
    assert "productivity_analysis" in result
    assert "peak_hours" in result["productivity_analysis"]
