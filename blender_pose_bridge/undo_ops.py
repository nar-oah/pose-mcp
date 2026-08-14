import bpy

from .armature import find_armature
from .errors import PoseBridgeError


def push_undo(message):
    if not bpy.ops.ed.undo_push.poll():
        raise PoseBridgeError("Blender Undo is unavailable in the current context")
    result = bpy.ops.ed.undo_push(message=message)
    if "FINISHED" not in result:
        raise PoseBridgeError(f"Blender could not create undo step: {message}")


def undo():
    armature = find_armature()
    armature_name = armature.name
    if not bpy.ops.ed.undo.poll():
        raise PoseBridgeError("Blender Undo is unavailable or the undo stack is empty")
    result = bpy.ops.ed.undo()
    if "FINISHED" not in result:
        raise PoseBridgeError("Blender could not undo the most recent operation")
    bpy.context.view_layer.update()
    return {
        "undone": True,
        "system": "Blender global undo",
        "armature": armature_name,
    }
