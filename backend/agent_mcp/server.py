"""FastMCP server — run from backend/: python -m agent_mcp.server"""

from fastmcp import FastMCP

from app.agent.tools import echo_message, get_current_time

mcp = FastMCP("local-agent-tools")


@mcp.tool()
def get_time() -> str:
    """Return current UTC time."""
    return get_current_time()


@mcp.tool()
def echo(message: str) -> str:
    """Echo a message back."""
    return echo_message(message)


if __name__ == "__main__":
    mcp.run()
