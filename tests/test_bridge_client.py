import unittest
from unittest.mock import patch

from blender_pose_mcp.bridge_client import BlenderOfflineError, BridgeClient


class BridgeClientTests(unittest.TestCase):
    @patch("blender_pose_mcp.bridge_client.socket.create_connection")
    def test_connection_refused_becomes_clear_offline_error(self, connect):
        connect.side_effect = ConnectionRefusedError
        with self.assertRaisesRegex(BlenderOfflineError, "127.0.0.1:8766"):
            BridgeClient().call("ping")


if __name__ == "__main__":
    unittest.main()
