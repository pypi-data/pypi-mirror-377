
def check_permission(agent, tool_name: str) -> bool:
    """Return True if the agent is allowed to use the given tool."""
    return tool_name in getattr(agent, "allowed_tools", [])
