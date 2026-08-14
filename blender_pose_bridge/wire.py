import json


def read_message(connection):
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
    try:
        message = json.loads(bytes(data).split(b"\n", 1)[0])
    except json.JSONDecodeError as exc:
        raise ValueError("Bridge request contains invalid JSON") from exc
    if not isinstance(message, dict):
        raise ValueError("Bridge request must be a JSON object")
    return message


def send_response(connection, response):
    try:
        connection.sendall(json.dumps(response).encode() + b"\n")
    except OSError:
        pass
