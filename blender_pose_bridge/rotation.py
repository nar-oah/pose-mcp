import math

from mathutils import Euler, Quaternion, Vector

from .errors import PoseBridgeError


def vector3(value, label="rotation_degrees"):
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise PoseBridgeError(f"{label} must contain exactly three numbers")
    if any(isinstance(item, bool) or not isinstance(item, (int, float)) for item in value):
        raise PoseBridgeError(f"{label} must contain exactly three numbers")
    result = [float(item) for item in value]
    if not all(math.isfinite(item) for item in result):
        raise PoseBridgeError(f"{label} values must be finite")
    return result


def current_quaternion(pose_bone):
    if pose_bone.rotation_mode == "QUATERNION":
        quaternion = pose_bone.rotation_quaternion.copy()
    elif pose_bone.rotation_mode == "AXIS_ANGLE":
        angle, x, y, z = pose_bone.rotation_axis_angle
        axis = Vector((x, y, z))
        quaternion = Quaternion(axis, angle) if axis.length else Quaternion()
    else:
        quaternion = pose_bone.rotation_euler.to_quaternion()
    quaternion.normalize()
    return quaternion


def degrees_quaternion(rotation_degrees):
    radians = [math.radians(value) for value in vector3(rotation_degrees)]
    return Euler(radians, "XYZ").to_quaternion()


def set_local_rotation(pose_bone, rotation_degrees, mode):
    if mode not in {"absolute", "delta"}:
        raise PoseBridgeError("mode must be 'absolute' or 'delta'")
    rotation = degrees_quaternion(rotation_degrees)
    rotation = current_quaternion(pose_bone) @ rotation if mode == "delta" else rotation
    rotation.normalize()
    pose_bone.rotation_mode = "QUATERNION"
    pose_bone.rotation_quaternion = rotation
