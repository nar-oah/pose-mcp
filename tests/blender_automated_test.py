import os
import sys
import unittest

import bpy

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from blender_pose_bridge.armature import find_armature
from blender_pose_bridge.errors import PoseBridgeError
from blender_pose_bridge.read_ops import get_pose, get_rig, ping


def make_armature(name, bone_name="head"):
    data = bpy.data.armatures.new(f"{name}Data")
    armature = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(armature)
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bone = data.edit_bones.new(bone_name)
    bone.head = (0, 0, 0)
    bone.tail = (0, 0, 1)
    bpy.ops.object.mode_set(mode="OBJECT")
    return armature


class BlenderBridgeTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def test_no_armature_is_explicit(self):
        with self.assertRaisesRegex(PoseBridgeError, "No Armature"):
            find_armature()

    def test_one_armature_is_selected_and_readable(self):
        armature = make_armature("Character")
        self.assertIs(find_armature(), armature)
        self.assertEqual(ping()["armature"], "Character")
        self.assertEqual(get_pose()["bones"][0]["bone"], "head")
        self.assertEqual(get_rig()["bones"][0]["semantic"], "head")

    def test_multiple_armatures_lists_names(self):
        make_armature("CharacterB")
        make_armature("CharacterA")
        with self.assertRaisesRegex(
            PoseBridgeError, r"\['CharacterA', 'CharacterB'\]"
        ):
            find_armature()


suite = unittest.defaultTestLoader.loadTestsFromTestCase(BlenderBridgeTests)
result = unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():
    raise SystemExit(1)
