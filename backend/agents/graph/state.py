import operator
from typing import TypedDict, Annotated, Any

class AnalysisState(TypedDict):
    user_id: int
    period_start: str
    period_end: str
    code_events: list[dict[str, Any]]
    git_events: list[dict[str, Any]]
    error_events: list[dict[str, Any]]
    terminal_events: list[dict[str, Any]]
    skill_analysis: dict[str, Any]
    productivity_analysis: dict[str, Any]
    debug_analysis: dict[str, Any]
    career_analysis: dict[str, Any]
    report: dict[str, Any]
    errors: Annotated[list[str], operator.add]
