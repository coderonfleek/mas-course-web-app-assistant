from typing import TypedDict, Optional

from .frontend import FRONTEND_SKILL
from .backend import BACKEND_SKILL
from .database import DATABASE_SKILL
from .network import NETWORK_SKILL

class Skill(TypedDict):
    name: str
    description: str
    content: str

SKILLS: list[Skill] = [
    FRONTEND_SKILL,
    BACKEND_SKILL,
    DATABASE_SKILL,
    NETWORK_SKILL
]

def get_skill(skill_name: str) -> Optional[Skill]:
    """Get a skill by name.
    
    Args:
        skill_name: The name of the skill to retrieve
        
    Returns:
        The skill dictionary if found, None otherwise
    """
    for skill in SKILLS:
        if skill["name"].lower() == skill_name.lower():
            return skill
    return None

def get_all_skills() -> list[Skill]:
    """Get all available skills.
    
    Returns:
        List of all skill dictionaries
    """
    return SKILLS

def get_all_skill_names() -> list[str]:
    """Get names of all available skills.
    
    Returns:
        List of skill names
    """
    return [skill["name"] for skill in SKILLS]

