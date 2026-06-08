import json
from langchain_core.messages import SystemMessage, HumanMessage
from agents.graph.state import AnalysisState
from agents.llm import get_llm

def productivity_agent(state: AnalysisState) -> dict:
    llm = get_llm()
    
    # We ideally want session data, but code_events have timestamps
    code_events_summary = json.dumps(state.get("code_events", [])[:50])
    
    system_prompt = """You are a Productivity Agent. 
Analyze the provided events to determine peak hours, session lengths, flow states, and context switches.
Return your analysis as a JSON object with this structure:
{
    "peak_hours": ["09:00", "10:00"],
    "avg_session_length": 120,
    "flow_states": 3,
    "context_switches": 5
}
Only return valid JSON."""

    human_prompt = f"Events: {code_events_summary}"
    
    try:
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)])
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        analysis = json.loads(content)
        return {"productivity_analysis": analysis}
    except Exception as e:
        return {"errors": [f"ProductivityAgent error: {str(e)}"]}
