import math

import bpy
from mathutils import Euler, Quaternion

from .armature import find_armature, pose_bone
from .constants import BODY_BONES, BODY_OFFSETS, HAND_BONES, ROOT_BONE
from .errors import PoseBridgeError
from .rotation import vector3
from .undo_ops import push_undo


# These conversion rules intentionally match reference/main.py.
def rotvec_to_quaternion(rv):
    angle = math.sqrt(rv[0] ** 2 + rv[1] ** 2 + rv[2] ** 2)
    if angle < 1e-8:
        return Quaternion((1, 0, 0, 0))
    s = math.sin(angle / 2) / angle
    return Quaternion((math.cos(angle / 2), rv[0] * s, rv[1] * s, rv[2] * s))


def set_bone_rot(pb, rotvec, is_root=False, is_hand=False, offset_euler=None):
    pb.rotation_mode = "QUATERNION"
    rv = [-v for v in rotvec] if is_hand else rotvec
    q_data = rotvec_to_quaternion(rv)
    if offset_euler:
        angles = [math.radians(value) for value in offset_euler]
        q_data = Euler(angles, "XYZ").to_quaternion() @ q_data
    conversion = Quaternion((1.0, 0.0, 0.0), math.radians(90))
    q_armature = conversion @ q_data @ conversion.inverted()
    root_fix = Quaternion((1.0, 0.0, 0.0), math.radians(180))
    q_armature = root_fix @ q_armature if is_root else q_armature
    basis = pb.bone.matrix_local.to_quaternion()
    pb.rotation_quaternion = basis.inverted() @ q_armature @ basis


def _rotvecs(data, key):
    values = data.get(key, [])
    if not isinstance(values, list):
        raise PoseBridgeError(f"{key} must be a list of rotation vectors")
    return [vector3(value, f"{key} rotation vector") for value in values]


def apply_smplx_pose(data):
    armature = find_armature()
    root_values = _rotvecs(data, "body_root_pose")
    if "body_root_pose" in data and len(root_values) != 1:
        raise PoseBridgeError("body_root_pose must contain exactly one rotation vector")
    body_values = _rotvecs(data, "body_pose")
    hand_values = {side: _rotvecs(data, f"{side[0]}hand_pose") for side in ("left", "right")}
    root = pose_bone(armature, ROOT_BONE) if root_values else None

    for bone in armature.pose.bones:
        bone.rotation_quaternion = (1, 0, 0, 0)
        bone.location = (0, 0, 0)
    if root:
        set_bone_rot(root, root_values[0], is_root=True)
    for name, rotvec in zip(BODY_BONES, body_values):
        if name in armature.pose.bones:
            set_bone_rot(
                armature.pose.bones[name], rotvec,
                offset_euler=BODY_OFFSETS.get(name, None),
            )
    for side in ("left", "right"):
        for name, rotvec in zip(HAND_BONES[side], hand_values[side]):
            if name in armature.pose.bones:
                set_bone_rot(armature.pose.bones[name], rotvec, is_hand=True)
    bpy.context.view_layer.update()
    push_undo("MCP Apply SMPL-X Pose")
    return {"armature": armature.name, "full_reset": True, "undo_steps": 1}
