from src.skills.registry import get_all_skills

def build_skills_prompt() -> str:
    """Build the skills section to inject into the system prompt.
    
    Returns:
        A formatted string listing all available skills with descriptions.
    """

    skills = get_all_skills()

    skills_list = []
    for skill in skills:
        skills_list.append(f"-**{skill['name']}**: {skill['description']}")

    skills_text = "\n".join(skills_list)

    return f"""

## Available Skills

You have access to specialized troubleshooting skills that you can load on-demand.
Each skill contains detailed diagnostic guides, common error patterns, and solutions.

{skills_text}

Use the `load_skill` tool when you need detailed information about a specific area.
You can load multiple skills if the problem spans multiple domains.
Always load the relevant skill(s) before providing detailed troubleshooting advice.
"""


def get_system_prompt() -> str:
    """Get the complete system prompt with skill descriptions injected.
        
    Returns:
        The full system prompt for the troubleshooting agent.
    """

    base_prompt = """You are an expert Web Application Troubleshooting Assistant.

Your role is to help developers diagnose and fix issues in their web applications.
You have deep knowledge of frontend, backend, database, and network troubleshooting.

## How to Help

1. Listen carefully to the developer's problem description
2. Identify which area(s) of the stack might be affected
3. Load the relevant skill(s) to access detailed troubleshooting guides
4. Ask clarifying questions if needed
5. Provide step-by-step diagnostic instructions
6. Suggest specific solutions based on the symptoms

## Guidelines

- Be systematic and thorough in your diagnosis
- Start with the most common causes before exploring edge cases
- Provide specific commands, code snippets, or configuration examples
- Explain WHY something might be failing, not just how to fix it
- If multiple skills might be relevant, load them to give comprehensive advice
"""
    skills_prompt = build_skills_prompt()

    return base_prompt + skills_prompt


class SkillMiddleware:
    """Middleware that provides the system prompt with skill descriptions.
    
    This class follows the middleware pattern but is simplified for our use case.
    The system prompt is built once and includes all skill descriptions.
    """

    def __init__(self):
        self.system_prompt = get_system_prompt()

    def get_system_prompt(self) -> str:

        return self.system_prompt