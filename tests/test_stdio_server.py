import sys
import unittest

from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client

from test_mcp_server import TOOL_NAMES


class StdioServerTests(unittest.IsolatedAsyncioTestCase):
    async def test_stdio_tools_list(self):
        parameters = StdioServerParameters(
            command=sys.executable,
            args=["-m", "blender_pose_mcp"],
        )
        async with Client(stdio_client(parameters)) as client:
            result = await client.list_tools()
        self.assertEqual({tool.name for tool in result.tools}, TOOL_NAMES)


if __name__ == "__main__":
    unittest.main()
