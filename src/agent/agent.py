import os 
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage

from .state import AgentState
from .middleware import SkillMiddleware
from src.tools.skill_tools import get_tools

# Load environment variables
load_dotenv()

def get_llm():
    """Get the configured LLM based on environment variables.
    
    Returns:
        A configured chat model instance.
    
    Raises:
        ValueError: If the LLM provider is not supported or API key is missing.
    """

    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        model = os.getenv("OPENAI_MODEL", "gpt-4o")
        return ChatOpenAI(model = model, api_key = api_key)
    
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        return ChatAnthropic(model = model, api_key = api_key)
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    
def create_troubleshooting_agent():

    """Create the troubleshooting agent with skills support.
    
    This function sets up:
    - The LLM with tool binding
    - The middleware for system prompt injection
    - The state graph with nodes and edges
    - Memory checkpointing for conversation persistence
    
    Returns:
        A compiled LangGraph agent ready for invocation.
    """

    # Initialize components
    llm = get_llm()
    middleware = SkillMiddleware()
    tools = get_tools()

    llm_with_tools = llm.bind_tools(tools)

    def agent_node(state: AgentState) -> dict: 
        """Process the current state and generate a response.
        
        Args:
            state: The current agent state with messages and loaded skills.
            
        Returns:
            Updated state with the agent's response.
        """

        system_message = SystemMessage(content=middleware.get_system_prompt())

        messages = [system_message] + state["messages"]

        response = llm_with_tools.invoke(messages)

        return {"messages": [response]}
    
    def tool_node(state: AgentState) -> dict:
        """Execute any tool calls from the agent's response.
        
        Args:
            state: The current agent state.
            
        Returns:
            Updated state with tool results and any skill tracking updates.
        """
        from langchain_core.messages import ToolMessage
        
        # Get the last message (should be an AIMessage with tool calls)
        last_message = state["messages"][-1]
        
        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return {"messages": [], "skills_loaded": state.get("skills_loaded", [])}
        
        tool_messages = []
        skills_loaded = list(state.get("skills_loaded", []))
        
        # Create a mapping of tool names to functions
        tool_map = {tool.name: tool for tool in tools}
        
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            if tool_name in tool_map:
                # Execute the tool
                result = tool_map[tool_name].invoke(tool_args)
                
                # Track loaded skills
                if tool_name == "load_skill":
                    skill_name = tool_args.get("skill_name", "")
                    if skill_name and skill_name not in skills_loaded:
                        skills_loaded.append(skill_name)
                
                tool_messages.append(
                    ToolMessage(
                        content=result,
                        tool_call_id=tool_call["id"]
                    )
                )
        
        # Update history with tool message and update the loaded skills
        return {"messages": tool_messages, "skills_loaded": skills_loaded}

    def should_continue(state: AgentState) -> str:
        """Determine whether to continue to tools or end.
        
        Args:
            state: The current agent state.
            
        Returns:
            "tools" if there are tool calls to process, "end" otherwise.
        """

        last_message = state["messages"][-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        
        return "end"
    
    # Build Graph
    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "agent")
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    graph.add_edge("tools", "agent")

    memory = MemorySaver()
    agent = graph.compile(checkpointer=memory)

    return agent

