import bpy

from .armature import find_armature
from .constants import BODY_BONES, HAND_BONES, ROOT_BONE, SEMANTIC_BONES
from .serialization import pose_bone_data, rig_bone_data


def ping():
    armature = find_armature()
    return {
        "blender_online": True,
        "blender_version": bpy.app.version_string,
        "blend_file": bpy.data.filepath or None,
        "armature": armature.name,
    }


def get_rig():
    armature = find_armature()
    return {
        "armature": armature.name,
        "root_bone": ROOT_BONE,
        "body_bones": BODY_BONES,
        "hand_bones": HAND_BONES,
        "semantic_mapping": SEMANTIC_BONES,
        "bones": [rig_bone_data(bone) for bone in armature.pose.bones],
    }


def get_pose():
    armature = find_armature()
    return {
        "armature": armature.name,
        "coordinate_spaces": {
            "rotation": "local pose-bone rotation; Euler order XYZ; degrees",
            "armature_position": "posed head/tail in Armature object space",
            "world_position": "posed head/tail after Armature matrix_world",
        },
        "armature_matrix_world": [
            [float(value) for value in row] for row in armature.matrix_world
        ],
        "bones": [
            pose_bone_data(armature, bone) for bone in armature.pose.bones
        ],
    }
