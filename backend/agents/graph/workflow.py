import logging
from langgraph.graph import StateGraph, START, END
from agents.graph.state import AnalysisState
from agents.skill_agent import skill_agent
from agents.productivity_agent import productivity_agent
from agents.debug_agent import debug_agent
from agents.career_agent import career_agent
from agents.report_agent import report_agent

logger = logging.getLogger(__name__)

def build_graph() -> Any:
    builder = StateGraph(AnalysisState)
    
    builder.add_node("skill", skill_agent)
    builder.add_node("productivity", productivity_agent)
    builder.add_node("debug", debug_agent)
    builder.add_node("career", career_agent)
    builder.add_node("report", report_agent)
    
    builder.add_edge(START, "skill")
    builder.add_edge("skill", "productivity")
    builder.add_edge("productivity", "debug")
    builder.add_edge("debug", "career")
    builder.add_edge("career", "report")
    builder.add_edge("report", END)
    
    return builder.compile()

def run_analysis(user_id: int, period_start: str, period_end: str) -> None:
    """Fetches events from DB, runs the LangGraph workflow, and publishes insights."""
    from telemetry.models import CodeEvent, GitEvent, ErrorEvent, TerminalEvent
    
    # In a real implementation, we would fetch events between period_start and period_end
    code_events = list(CodeEvent.objects.filter(session__user_id=user_id).values()[:100])
    git_events = list(GitEvent.objects.filter(session__user_id=user_id).values()[:100])
    error_events = list(ErrorEvent.objects.filter(session__user_id=user_id).values()[:100])
    terminal_events = list(TerminalEvent.objects.filter(session__user_id=user_id).values()[:100])
    
    state = AnalysisState(
        user_id=user_id,
        period_start=period_start,
        period_end=period_end,
        code_events=code_events,
        git_events=git_events,
        error_events=error_events,
        terminal_events=terminal_events,
        skill_analysis={},
        productivity_analysis={},
        debug_analysis={},
        career_analysis={},
        report={},
        errors=[]
    )
    
    graph = build_graph()
    try:
        result = graph.invoke(state)
        
        # In a real implementation, we would publish the results to Kafka topics
        # e.g., 'skill-insights', 'weekly-reports'
        # For now we can just log the completion
        logger.info(f"Analysis completed for user {user_id}. Report title: {result.get('report', {}).get('title', 'Unknown')}")
        if result.get("errors"):
            logger.error(f"Analysis errors: {result['errors']}")
            
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
