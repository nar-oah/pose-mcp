import threading
from dataclasses import dataclass, field


@dataclass
class PendingRequest:
    request_id: object
    method: str
    params: dict
    done: threading.Event = field(default_factory=threading.Event)
    result: object = None
    error: str | None = None
