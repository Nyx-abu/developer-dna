import json
from langchain_core.messages import SystemMessage, HumanMessage
from agents.graph.state import AnalysisState
from agents.llm import get_llm

def skill_agent(state: AnalysisState) -> dict:
    llm = get_llm()
    code_events_summary = json.dumps(state.get("code_events", [])[:50]) # limit context size
    
    system_prompt = """You are a Skill Assessment Agent. 
Analyze the provided code events to assess the developer's language usage, file patterns, and complexity.
Return your analysis as a JSON object with the following structure:
{
    "languages": {"python": {"lines_written": 1500, "primary": true}},
    "proficiency_scores": {"python": 85},
    "evidence": ["Wrote complex python logic across 15 files"]
}
Only return valid JSON."""

    human_prompt = f"Code Events: {code_events_summary}"
    
    try:
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)])
        
        # Parse JSON
        content = response.content
        if hasattr(response, "content"):
            content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        analysis = json.loads(content)
        return {"skill_analysis": analysis}
    except Exception as e:
        return {"errors": [f"SkillAgent error: {str(e)}"]}
