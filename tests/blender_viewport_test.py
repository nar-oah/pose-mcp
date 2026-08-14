import os
import sys

import bpy

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from blender_pose_bridge.file_ops import get_viewport


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


filepath = None
try:
    make_armature()
    result = get_viewport()
    filepath = result["path"]
    assert result["mime_type"] == "image/png", result
    assert result["size_bytes"] > 0, result
    assert os.path.isfile(filepath), result
    print(f"Blender VIEW_3D capture: OK ({result['size_bytes']} bytes)")
finally:
    if filepath and os.path.isfile(filepath):
        os.unlink(filepath)
    bpy.ops.wm.quit_blender()
