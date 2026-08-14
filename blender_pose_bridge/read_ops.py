import bpy

from .armature import find_armature
from .constants import BODY_BONES, HAND_BONES, ROOT_BONE, SEMANTIC_BONES
from .serialization import bone_state, rig_bone_data


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
        "space": "local pose-bone rotation; Euler order XYZ; angles in degrees",
        "bones": [bone_state(bone) for bone in armature.pose.bones],
    }
