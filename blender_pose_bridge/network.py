import json
import queue
import socket
import threading
import time
from dataclasses import dataclass, field


@dataclass
class PendingRequest:
    request_id: object
    method: str
    params: dict
    done: threading.Event = field(default_factory=threading.Event)
    result: object = None
    error: str | None = None


class BridgeSocketServer:
    def __init__(self, host, port, request_timeout=30.0):
        self.host = host
        self.port = port
        self.request_timeout = request_timeout
        self.requests = queue.Queue()
        self.stop_event = threading.Event()
        self.ready = threading.Event()
        self.thread = None
        self.server_socket = None
        self.last_error = None

    @property
    def online(self):
        return self.ready.is_set() and self.thread is not None and self.thread.is_alive()

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.stop_event.clear()
        self.thread = threading.Thread(
            target=self._serve, name="BlenderPoseBridge", daemon=True
        )
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.ready.clear()
        if self.server_socket:
            self.server_socket.close()
        if self.thread:
            self.thread.join(timeout=2.0)
        self.thread = None
        self.server_socket = None

    def _serve(self):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.host, self.port))
            server.listen(8)
            server.settimeout(0.5)
            self.server_socket = server
            self.last_error = None
            self.ready.set()
            while not self.stop_event.is_set():
                try:
                    connection, _address = server.accept()
                except socket.timeout:
                    continue
                with connection:
                    self._handle_connection(connection)
        except OSError as exc:
            if not self.stop_event.is_set():
                self.last_error = str(exc)
        finally:
            self.ready.clear()

    def _handle_connection(self, connection):
        request_id = None
        try:
            message = self._read_message(connection)
            request_id = message.get("id")
            pending = PendingRequest(
                request_id, message.get("method"), message.get("params", {})
            )
            self.requests.put(pending)
            deadline = time.monotonic() + self.request_timeout
            while not pending.done.wait(0.05):
                if self.stop_event.is_set() or time.monotonic() >= deadline:
                    pending.error = "Blender main thread timed out processing the request"
                    break
            response = {"id": request_id, "ok": pending.error is None}
            response["error" if pending.error else "result"] = pending.error or pending.result
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            response = {"id": request_id, "ok": False, "error": str(exc)}
        connection.sendall(json.dumps(response).encode() + b"\n")

    @staticmethod
    def _read_message(connection):
        connection.settimeout(5.0)
        data = bytearray()
        while b"\n" not in data:
            chunk = connection.recv(65536)
            if not chunk:
                break
            data.extend(chunk)
            if len(data) > 16 * 1024 * 1024:
                raise ValueError("Bridge request exceeded 16 MiB")
        if not data:
            raise ValueError("Empty Bridge request")
        message = json.loads(bytes(data).split(b"\n", 1)[0])
        if not isinstance(message, dict):
            raise ValueError("Bridge request must be a JSON object")
        return message

    def drain(self, handler, limit=8):
        for _index in range(limit):
            try:
                pending = self.requests.get_nowait()
            except queue.Empty:
                break
            try:
                pending.result = handler(pending.method, pending.params)
            except Exception as exc:
                pending.error = str(exc)
            finally:
                pending.done.set()
