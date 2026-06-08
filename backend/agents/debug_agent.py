import json
from langchain_core.messages import SystemMessage, HumanMessage
from agents.graph.state import AnalysisState
from agents.llm import get_llm

def debug_agent(state: AnalysisState) -> dict:
    llm = get_llm()
    error_events_summary = json.dumps(state.get("error_events", [])[:50])
    
    system_prompt = """You are a Debug Agent. 
Analyze the provided error events for patterns, resolution times, and frequency.
Return your analysis as a JSON object with this structure:
{
    "error_frequency": {"SyntaxError": 5, "TypeError": 2},
    "mean_resolution_time": 45,
    "recurring_patterns": ["Often forgets imports in python"],
    "efficiency_score": 75
}
Only return valid JSON."""

    human_prompt = f"Error Events: {error_events_summary}"
    
    try:
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)])
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        analysis = json.loads(content)
        return {"debug_analysis": analysis}
    except Exception as e:
        return {"errors": [f"DebugAgent error: {str(e)}"]}
