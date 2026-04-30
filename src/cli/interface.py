import uuid
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from langchain_core.messages import HumanMessage, AIMessage

from src.agent import create_troubleshooting_agent
from src.skills import get_all_skills

console = Console()

# Display Functions
def print_welcome():
    """Print the welcome message and instructions."""
    welcome_text = """
[bold cyan]🔧 Web App Troubleshooting Assistant[/bold cyan]

I help debug web application issues across the full stack.
Just describe your problem and I'll help diagnose it.

[dim]Type [bold]/help[/bold] for available commands
Type [bold]/quit[/bold] to exit[/dim]
"""
    console.print(Panel(welcome_text, border_style="cyan"))

def print_help():
    """Print available commands."""
    table = Table(title="Available Commands", border_style="cyan")
    table.add_column("Command", style="bold cyan")
    table.add_column("Description")
    
    table.add_row("/help", "Show this help message")
    table.add_row("/skills", "List all available troubleshooting skills")
    table.add_row("/loaded", "Show skills loaded in current session")
    table.add_row("/clear", "Clear conversation history and start fresh")
    table.add_row("/quit, /exit", "Exit the assistant")
    
    console.print(table)

def print_skills():
    """Print all available skills."""
    skills = get_all_skills()
    
    table = Table(title="Available Skills", border_style="green")
    table.add_column("Skill", style="bold green")
    table.add_column("Description")
    
    for skill in skills:
        table.add_row(skill["name"], skill["description"])
    
    console.print(table)

def print_loaded_skills(skills_loaded: list[str]):
    """Print skills loaded in current session."""
    if not skills_loaded:
        console.print("[dim]No skills loaded yet in this session.[/dim]")
        return
    
    table = Table(title="Loaded Skills (This Session)", border_style="yellow")
    table.add_column("Skill", style="bold yellow")
    
    for skill in skills_loaded:
        table.add_row(skill)
    
    console.print(table)

def print_response(response: str):
    """Print the assistant's response with markdown formatting."""
    md = Markdown(response)
    console.print(Panel(md, title="[bold green]Assistant[/bold green]", border_style="green"))

def print_error(message: str):
    """Print an error message."""
    console.print(f"[bold red]Error:[/bold red] {message}")

# Skill Loading Functions

def extract_loaded_skills_from_messages(messages: list, previous_skills: list[str]) -> list[str]:
    """Extract skill names that were loaded from tool calls in messages.
    
    Args:
        messages: List of messages from the agent response
        previous_skills: Skills that were already loaded before this query
        
    Returns:
        List of newly loaded skill names
    """
    newly_loaded = []
    
    for msg in messages:
        # Check for AIMessage with tool calls
        if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
            for tool_call in msg.tool_calls:
                if tool_call.get("name") == "load_skill":
                    skill_name = tool_call.get("args", {}).get("skill_name", "")
                    if skill_name and skill_name not in previous_skills and skill_name not in newly_loaded:
                        newly_loaded.append(skill_name)
    
    return newly_loaded


def print_skill_loading(skill_names: list[str]):
    """Print notification when skills are being loaded.
    
    Args:
        skill_names: List of skill names that were loaded
    """
    if not skill_names:
        return
    
    skills_str = ", ".join([f"[bold yellow]{name}[/bold yellow]" for name in skill_names])
    console.print(f"\n[dim]📚 Loading skill(s): {skills_str}[/dim]")


def print_skills_loaded_summary(newly_loaded: list[str], all_loaded: list[str]):
    """Print a summary of skills loaded for this query.
    
    Args:
        newly_loaded: Skills loaded during this query
        all_loaded: All skills loaded in the session so far
    """
    if newly_loaded:
        skills_str = ", ".join([f"[bold green]{name}[/bold green]" for name in newly_loaded])
        console.print(f"[dim]✓ Loaded: {skills_str}[/dim]")
        
        if len(all_loaded) > len(newly_loaded):
            other_skills = [s for s in all_loaded if s not in newly_loaded]
            if other_skills:
                other_str = ", ".join(other_skills)
                console.print(f"[dim]  (Previously loaded: {other_str})[/dim]")
        console.print()

def run_cli():
    """Run the interactive CLI loop"""

    print_welcome()

    # Create the agent
    try:
        with console.status("[bold cyan]Initializing agent...[/bold cyan]"):
            agent = create_troubleshooting_agent()
    except ValueError as e:
        print_error(str(e))
        console.print("\n[dim]Please check your .env file and try again.[/dim]")
        return
    except Exception as e:
        print_error(f"Failed to initialize agent: {e}")
        return

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    skills_loaded = []

    console.print("[dim]Agent Ready! Describe your problem. [/dim]\n")

    while True:
        try:
            # Get user input
            user_input = console.input("[bold cyan]You:[/bold cyan] ").strip()

            if not user_input:
                continue

                        # Handle commands
            if user_input.startswith("/"):
                command = user_input.lower()

                if command in ["/quit", "/exit"]:
                    console.print("\n[dim]Goodbye! Happy debugging! 🔧[/dim]")
                    break

                elif command == "/help":
                    print_help()
                    continue

                elif command == "/skills":
                    print_skills()
                    continue

                elif command == "/loaded":
                    print_loaded_skills(skills_loaded)
                    continue

                elif command == "/clear":
                    thread_id = str(uuid.uuid4())
                    config = {"configurable": {"thread_id": thread_id}}
                    skills_loaded = []
                    console.print("[dim]Conversation cleared. Starting fresh![/dim]\n")
                    continue

                else:
                    console.print(f"[dim]Unknown command: {user_input}. Type /help for available commands.[/dim]")
                    continue

            skills_before = list(skills_loaded)

            with console.status("[bold cyan]Analyzing your problem...[/bold cyan]"):
                result = agent.invoke(
                    {"messages": [HumanMessage(content=user_input)]},
                    config
                )

            newly_loaded = extract_loaded_skills_from_messages(
                result["messages"],
                skills_before
            )

            #  Update loaded skills from state
            if "skills_loaded" in result:
                skills_loaded = result["skills_loaded"]
            else:
                # Fallback: add newly loaded to our tracking
                for skill in newly_loaded:
                    skills_loaded.append(skill)

            # Show skills that were loaded for this query
            if newly_loaded:
                print_skills_loaded_summary(newly_loaded, skills_loaded)

            last_message = None
            for msg in reversed(result["messages"]):
                if isinstance(msg, AIMessage) and msg.content:
                    last_message = msg
                    break

            if last_message:
                print_response(last_message.content)
            else:
                console.print("[dim]No response generated[/dim]")

            console.print()

        except ValueError as e:
            print_error(str(e))
            console.print("\n[dim]Please check your .env file and try again.[/dim]")
            return
        except Exception as e:
            print_error(f"Failed to initialize agent: {e}")
            return
        

if __name__ == "__main__":
    run_cli()