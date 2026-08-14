import json
import socket
import uuid
from typing import Any


class BridgeError(RuntimeError):
    """An error reported by the Blender add-on."""


class BlenderOfflineError(BridgeError):
    """The local Blender Pose Bridge is not reachable."""


class BridgeClient:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8766,
        timeout: float = 30.0,
    ) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout

    def call(self, method: str, params: dict[str, Any] | None = None) -> Any:
        request = {
            "id": uuid.uuid4().hex,
            "method": method,
            "params": params or {},
        }
        payload = json.dumps(request, separators=(",", ":")).encode() + b"\n"
        try:
            with socket.create_connection(
                (self.host, self.port), timeout=self.timeout
            ) as connection:
                connection.settimeout(self.timeout)
                connection.sendall(payload)
                response = self._read_response(connection)
        except (ConnectionError, OSError, TimeoutError) as exc:
            raise BlenderOfflineError(
                f"Blender Pose Bridge is offline at {self.host}:{self.port}. "
                "Enable the Blender Pose Bridge add-on."
            ) from exc
        if response.get("id") != request["id"]:
            raise BridgeError("Blender Pose Bridge returned a mismatched request id")
        if not response.get("ok"):
            raise BridgeError(str(response.get("error", "Unknown Blender bridge error")))
        return response.get("result")

    def _read_response(self, connection: socket.socket) -> dict[str, Any]:
        data = bytearray()
        while b"\n" not in data:
            chunk = connection.recv(65536)
            if not chunk:
                break
            data.extend(chunk)
            if len(data) > 32 * 1024 * 1024:
                raise BridgeError("Blender Pose Bridge response exceeded 32 MiB")
        if not data:
            raise BridgeError("Blender Pose Bridge returned an empty response")
        try:
            response = json.loads(bytes(data).split(b"\n", 1)[0])
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BridgeError("Blender Pose Bridge returned invalid JSON") from exc
        if not isinstance(response, dict):
            raise BridgeError("Blender Pose Bridge response must be a JSON object")
        return response
