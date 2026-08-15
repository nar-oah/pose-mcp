import math

from .constants import bone_groups, semantic_name
from .rotation import current_quaternion


def _floats(values):
    return [float(value) for value in values]


def _matrix_rows(matrix):
    return [[float(value) for value in row] for row in matrix]


def _constraint_data(constraint):
    data = {
        "name": constraint.name,
        "type": constraint.type,
        "influence": float(constraint.influence),
        "mute": bool(constraint.mute),
        "is_valid": bool(constraint.is_valid),
    }
    for field in ("subtarget", "pole_subtarget", "chain_count", "use_tail"):
        if hasattr(constraint, field):
            data[field] = getattr(constraint, field)
    for field in ("target", "pole_target"):
        if hasattr(constraint, field):
            target = getattr(constraint, field)
            data[field] = target.name if target else None
    return data


def bone_state(pose_bone):
    quaternion = current_quaternion(pose_bone)
    euler = quaternion.to_euler("XYZ")
    return {
        "bone": pose_bone.name,
        "semantic": semantic_name(pose_bone.name),
        "groups": bone_groups(pose_bone.name),
        "euler_degrees": [math.degrees(value) for value in euler],
        "quaternion": _floats(quaternion),
        "rotation_mode": pose_bone.rotation_mode,
        "location": _floats(pose_bone.location),
        "scale": _floats(pose_bone.scale),
    }


def pose_bone_data(armature, pose_bone):
    to_world = armature.matrix_world
    data = bone_state(pose_bone)
    data.update(
        {
            "parent": pose_bone.parent.name if pose_bone.parent else None,
            "head_position": {
                "armature": _floats(pose_bone.head),
                "world": _floats(to_world @ pose_bone.head),
            },
            "tail_position": {
                "armature": _floats(pose_bone.tail),
                "world": _floats(to_world @ pose_bone.tail),
            },
        }
    )
    return data


def rig_bone_data(pose_bone):
    bone = pose_bone.bone
    constraints = [_constraint_data(item) for item in pose_bone.constraints]
    data = bone_state(pose_bone)
    data.update(
        {
            "parent": bone.parent.name if bone.parent else None,
            "children": [child.name for child in bone.children],
            "rest": {
                "matrix_local": _matrix_rows(bone.matrix_local),
                "head_local": _floats(bone.head_local),
                "tail_local": _floats(bone.tail_local),
            },
            "constraints": constraints,
            "has_ik_constraint": any(
                constraint.type in {"IK", "SPLINE_IK"}
                for constraint in pose_bone.constraints
            ),
        }
    )
    return data
