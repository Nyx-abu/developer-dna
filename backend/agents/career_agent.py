import json
from langchain_core.messages import SystemMessage, HumanMessage
from agents.graph.state import AnalysisState
from agents.llm import get_llm

def career_agent(state: AnalysisState) -> dict:
    llm = get_llm()
    
    # Synthesize previous analyses
    synthesis_context = json.dumps({
        "skills": state.get("skill_analysis", {}),
        "productivity": state.get("productivity_analysis", {}),
        "debug": state.get("debug_analysis", {})
    })
    
    system_prompt = """You are a Career Agent. 
Synthesize the provided skill, productivity, and debug analyses.
Return your analysis as a JSON object with this structure:
{
    "trajectory": "Senior Backend Engineer",
    "skill_gaps": ["Kubernetes", "GraphQL"],
    "recommendations": ["Focus on system design", "Improve debug efficiency"],
    "strengths": ["Python expertise", "High productivity during mornings"]
}
Only return valid JSON."""

    human_prompt = f"Analyses: {synthesis_context}"
    
    try:
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)])
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        analysis = json.loads(content)
        return {"career_analysis": analysis}
    except Exception as e:
        return {"errors": [f"CareerAgent error: {str(e)}"]}
