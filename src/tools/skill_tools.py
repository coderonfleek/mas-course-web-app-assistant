from langchain_core.tools import tool
from src.skills.registry import get_skill, get_all_skill_names

@tool
def load_skill(skill_name: str) -> str:
    """Load a specialized troubleshooting skill into the conversation context.
    
    Use this tool when you need detailed diagnostic information about a specific
    area of web application troubleshooting. Each skill contains comprehensive
    guides, common error patterns, and step-by-step solutions.
    
    Available skills:
    - frontend: Browser rendering, JavaScript errors, React/Vue issues, CSS problems
    - backend: Server errors, API failures, Express/FastAPI/Django debugging
    - database: Connection issues, query problems, ORM debugging, migrations
    - network: CORS, SSL/TLS, DNS, timeouts, proxy configuration
    
    Args:
        skill_name: The name of the skill to load (e.g., "frontend", "backend")
        
    Returns:
        The full skill content with troubleshooting guides, or an error message
        if the skill is not found.
    """

    skill = get_skill(skill_name)

    if skill is None:
        available = ", ".join(get_all_skill_names())
        return f"Skill '{skill_name}' not found. Available skills: {available}"
    
    return f"""
================================================================================
SKILL LOADED: {skill['name'].upper()}
================================================================================

{skill['content']}

================================================================================
END OF SKILL: {skill['name'].upper()}
================================================================================
"""

def get_tools() -> list:
    """Get all available tools for the agent

    Return:
        A list of tool instances that can be bound to the LLM
    """
    return [load_skill]



