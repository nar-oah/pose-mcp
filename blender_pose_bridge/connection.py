import time

from .pending import PendingRequest
from .wire import read_message, send_response


def handle_connection(connection, requests, stop_event, request_timeout):
    request_id = None
    try:
        message = read_message(connection)
        request_id = message.get("id")
        pending = PendingRequest(
            request_id, message.get("method"), message.get("params", {})
        )
        requests.put(pending)
        deadline = time.monotonic() + request_timeout
        while not pending.done.wait(0.05):
            if stop_event.is_set() or time.monotonic() >= deadline:
                pending.error = "Blender main thread timed out processing the request"
                pending.cancelled = True
                break
        response = {"id": request_id, "ok": pending.error is None}
        response["error" if pending.error else "result"] = pending.error or pending.result
    except (ValueError, OSError) as exc:
        response = {"id": request_id, "ok": False, "error": str(exc)}
    send_response(connection, response)
