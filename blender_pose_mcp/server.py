from mcp.server import MCPServer

from .bridge_client import BridgeClient
from .instructions import SERVER_INSTRUCTIONS
from .tools import register_tools


def create_server(bridge: BridgeClient | None = None) -> MCPServer:
    server = MCPServer(
        "blender-pose",
        description="Dedicated MCP server for posing one existing Blender Armature",
        instructions=SERVER_INSTRUCTIONS,
        version="0.1.0",
        log_level="WARNING",
    )
    register_tools(server, bridge or BridgeClient())
    return server


mcp = create_server()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
