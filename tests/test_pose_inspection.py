import base64
import tempfile
import unittest
from pathlib import Path

from mcp import Client

from blender_pose_mcp.server import create_server


class SnapshotBridge:
    def __init__(self, snapshot):
        self.snapshot = snapshot
        self.calls = []

    def call(self, method, params=None):
        self.calls.append((method, params or {}))
        return self.snapshot


class PoseInspectionTests(unittest.IsolatedAsyncioTestCase):
    async def test_viewport_returns_pose_and_four_image_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            views = []
            for name, axis in (
                ("front", "FRONT"),
                ("left", "LEFT"),
                ("right", "RIGHT"),
                ("back", "BACK"),
            ):
                path = Path(directory, f"{name}.png")
                path.write_bytes(b"png-data")
                views.append(
                    {
                        "name": name,
                        "axis": axis,
                        "projection": "orthographic",
                        "path": str(path),
                        "mime_type": "image/png",
                        "size_bytes": 8,
                    }
                )
            snapshot = {
                "armature": "Character",
                "pose": {"bones": [{"bone": "head"}]},
                "views": views,
                "temporary": True,
            }
            bridge = SnapshotBridge(snapshot)
            async with Client(create_server(bridge)) as client:
                result = await client.call_tool("get_viewport", {})
        images = [item for item in result.content if item.type == "image"]
        self.assertFalse(result.is_error)
        self.assertEqual(result.structured_content, snapshot)
        self.assertEqual(len(images), 4)
        self.assertEqual(base64.b64decode(images[0].data), b"png-data")
        self.assertEqual(bridge.calls, [("get_viewport", {})])


if __name__ == "__main__":
    unittest.main()
