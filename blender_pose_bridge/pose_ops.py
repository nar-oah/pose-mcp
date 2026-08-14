import bpy
from mathutils import Matrix

from .armature import find_armature, pose_bone
from .errors import PoseBridgeError
from .rotation import set_local_rotation, vector3
from .serialization import bone_state
from .undo_ops import ensure_undo, push_undo


def _validate_change(armature, change):
    if not isinstance(change, dict):
        raise PoseBridgeError("Each changes item must be a JSON object")
    name = change.get("bone")
    if not isinstance(name, str) or not name:
        raise PoseBridgeError("bone must be a non-empty string")
    bone = pose_bone(armature, name)
    rotation = vector3(change.get("rotation_degrees"))
    mode = change.get("mode", "absolute")
    if mode not in {"absolute", "delta"}:
        raise PoseBridgeError("mode must be 'absolute' or 'delta'")
    return bone, rotation, mode


def set_pose_batch(params):
    changes = params.get("changes")
    if not isinstance(changes, list) or not changes:
        raise PoseBridgeError("changes must be a non-empty list")
    if len(changes) > 256:
        raise PoseBridgeError("changes cannot contain more than 256 items")
    armature = find_armature()
    validated = [_validate_change(armature, change) for change in changes]
    ensure_undo()
    for bone, rotation, mode in validated:
        set_local_rotation(bone, rotation, mode)
    armature.update_tag()
    bpy.context.view_layer.update()
    push_undo("MCP Pose Batch")
    return {
        "armature": armature.name,
        "changed": [bone_state(item[0]) for item in validated],
        "undo_steps": 1,
    }


def set_bone_pose(params):
    result = set_pose_batch({"changes": [params]})
    result["changed"] = result["changed"][0]
    return result


def reset_pose(params):
    if params.get("scope", "all") != "all":
        raise PoseBridgeError("scope must be 'all'")
    armature = find_armature()
    ensure_undo()
    for bone in armature.pose.bones:
        bone.matrix_basis = Matrix.Identity(4)
    armature.update_tag()
    bpy.context.view_layer.update()
    push_undo("MCP Reset Pose")
    return {
        "armature": armature.name,
        "scope": "all",
        "reset_bones": len(armature.pose.bones),
        "undo_steps": 1,
    }
