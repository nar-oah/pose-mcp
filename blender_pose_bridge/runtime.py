import bpy

from .constants import HOST, PORT
from .handlers import dispatch
from .network import BridgeSocketServer

_server = None


def get_server():
    return _server


def _drain_requests():
    if _server is None:
        return None
    _server.drain(dispatch)
    return 0.05


def start():
    global _server
    if _server and _server.thread and _server.thread.is_alive():
        return _server
    if _server:
        _server.stop()
    _server = BridgeSocketServer(HOST, PORT)
    _server.start()
    if not bpy.app.timers.is_registered(_drain_requests):
        bpy.app.timers.register(_drain_requests, first_interval=0.05, persistent=True)
    return _server


def stop():
    global _server
    if bpy.app.timers.is_registered(_drain_requests):
        bpy.app.timers.unregister(_drain_requests)
    if _server:
        _server.stop()
    _server = None
