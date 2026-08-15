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


filepaths = []
try:
    make_armature()
    result = get_viewport()
    filepaths = [view["path"] for view in result["views"]]
    assert [view["name"] for view in result["views"]] == [
        "front", "left", "right", "back"
    ], result
    assert all(view["mime_type"] == "image/png" for view in result["views"])
    assert all(view["size_bytes"] > 0 for view in result["views"]), result
    assert all(view["height"] <= 768 for view in result["views"]), result
    assert all(os.path.isfile(filepath) for filepath in filepaths), result
    assert result["pose"]["bones"][0]["bone"] == "head", result
    size = sum(view["size_bytes"] for view in result["views"])
    print(f"Blender fixed multi-view capture: OK ({size} bytes)")
finally:
    for filepath in filepaths:
        if os.path.isfile(filepath):
            os.unlink(filepath)
    bpy.ops.wm.quit_blender()
