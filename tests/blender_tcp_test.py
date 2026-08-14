import json
import os
import socket
import sys
import threading
import time

import bpy

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import blender_pose_bridge
from blender_pose_bridge.handlers import dispatch


def make_armature():
    data = bpy.data.armatures.new("CharacterData")
    armature = bpy.data.objects.new("Character", data)
    bpy.context.scene.collection.objects.link(armature)
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bone = data.edit_bones.new("head")
    bone.tail = (0, 0, 1)
    bpy.ops.object.mode_set(mode="OBJECT")


def request_ping(output, done):
    request = {"id": "tcp-test", "method": "ping", "params": {}}
    with socket.create_connection(("127.0.0.1", 8766), timeout=5) as connection:
        connection.sendall(json.dumps(request).encode() + b"\n")
        data = bytearray()
        while b"\n" not in data:
            data.extend(connection.recv(65536))
    output.update(json.loads(bytes(data).split(b"\n", 1)[0]))
    done.set()


bpy.ops.wm.read_factory_settings(use_empty=True)
make_armature()
blender_pose_bridge.register()
server = blender_pose_bridge.runtime.get_server()
if not server.ready.wait(5):
    raise RuntimeError(f"Bridge failed to listen: {server.last_error}")

output = {}
done = threading.Event()
client = threading.Thread(target=request_ping, args=(output, done), daemon=True)
client.start()
deadline = time.monotonic() + 5
while not done.is_set() and time.monotonic() < deadline:
    server.drain(dispatch)
    time.sleep(0.01)
client.join(timeout=1)
blender_pose_bridge.unregister()

assert output["ok"] is True, output
assert output["result"]["blender_online"] is True, output
assert output["result"]["armature"] == "Character", output
print("Blender Pose Bridge TCP ping: OK")
