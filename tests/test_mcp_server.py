import unittest

from mcp import Client

from blender_pose_mcp.bridge_client import BlenderOfflineError, BridgeError
from blender_pose_mcp.server import create_server

TOOL_NAMES = {
    "ping", "get_rig", "get_pose", "set_bone_pose", "set_pose_batch",
    "apply_smplx_pose", "reset_pose", "undo", "get_viewport", "save_blend",
}


class FakeBridge:
    def __init__(self, error=None):
        self.error = error
        self.calls = []

    def call(self, method, params=None):
        self.calls.append((method, params or {}))
        if self.error:
            raise self.error
        if method == "ping":
            return {
                "blender_online": True,
                "blender_version": "5.2.0",
                "blend_file": "/tmp/pose.blend",
                "armature": "Character",
            }
        return {"method": method, "params": params or {}}


class MCPServerTests(unittest.IsolatedAsyncioTestCase):
    async def test_tools_list_contains_only_pose_tools(self):
        async with Client(create_server(FakeBridge())) as client:
            result = await client.list_tools()
        self.assertEqual({tool.name for tool in result.tools}, TOOL_NAMES)

    async def test_ping_traverses_bridge(self):
        bridge = FakeBridge()
        async with Client(create_server(bridge)) as client:
            result = await client.call_tool("ping", {})
        self.assertFalse(result.is_error)
        self.assertEqual(result.structured_content["armature"], "Character")
        self.assertEqual(bridge.calls, [("ping", {})])

    async def test_invalid_rotation_vector_is_rejected(self):
        bridge = FakeBridge()
        async with Client(create_server(bridge)) as client:
            result = await client.call_tool(
                "set_bone_pose",
                {"bone": "head", "rotation_degrees": [1, 2], "mode": "delta"},
            )
        self.assertTrue(result.is_error)
        self.assertEqual(bridge.calls, [])

    async def test_invalid_mode_is_rejected(self):
        bridge = FakeBridge()
        async with Client(create_server(bridge)) as client:
            result = await client.call_tool(
                "set_bone_pose",
                {"bone": "head", "rotation_degrees": [1, 2, 3], "mode": "world"},
            )
        self.assertTrue(result.is_error)
        self.assertEqual(bridge.calls, [])

    async def _assert_bridge_error(self, error, expected):
        async with Client(create_server(FakeBridge(error))) as client:
            result = await client.call_tool("get_rig", {})
        self.assertTrue(result.is_error)
        self.assertIn(expected, result.content[0].text)

    async def test_blender_offline_error(self):
        await self._assert_bridge_error(
            BlenderOfflineError("Blender Pose Bridge is offline"), "offline"
        )

    async def test_no_armature_error(self):
        await self._assert_bridge_error(
            BridgeError("No Armature object exists in the current scene"), "No Armature"
        )

    async def test_multiple_armatures_error_lists_names(self):
        await self._assert_bridge_error(
            BridgeError("Multiple Armature objects found: ['A', 'B']"), "['A', 'B']"
        )


if __name__ == "__main__":
    unittest.main()
