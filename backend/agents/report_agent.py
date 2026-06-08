import json
from langchain_core.messages import SystemMessage, HumanMessage
from agents.graph.state import AnalysisState
from agents.llm import get_llm

def report_agent(state: AnalysisState) -> dict:
    llm = get_llm()
    
    context = json.dumps({
        "skills": state.get("skill_analysis", {}),
        "productivity": state.get("productivity_analysis", {}),
        "debug": state.get("debug_analysis", {}),
        "career": state.get("career_analysis", {})
    })
    
    system_prompt = """You are a Report Agent generating a Spotify-Wrapped-style narrative for developers. 
Synthesize all analyses into a final comprehensive report.
Return your report as a JSON object with this structure:
{
    "title": "Your Developer DNA: 2024 Week 42",
    "summary": "A productive week with a focus on Python backend.",
    "highlights": ["1500 lines of Python written", "Reached Senior level proficiency"],
    "badges": ["Night Owl", "Bug Squasher"],
    "tips": ["Take more breaks during peak hours"],
    "detailed_sections": {"skills": "...", "productivity": "..."}
}
Only return valid JSON."""

    human_prompt = f"Data: {context}"
    
    try:
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)])
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        report = json.loads(content)
        return {"report": report}
    except Exception as e:
        return {"errors": [f"ReportAgent error: {str(e)}"]}
