import os
import sys
import unittest

import bpy

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from blender_pose_bridge.armature import find_armature
from blender_pose_bridge.errors import PoseBridgeError
from blender_pose_bridge.pose_ops import reset_pose, set_bone_pose
from blender_pose_bridge.read_ops import get_pose, get_rig, ping
from blender_pose_bridge.undo_ops import undo


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
        armature.pose.bones["head"].constraints.new("IK")
        self.assertIs(find_armature(), armature)
        self.assertEqual(ping()["armature"], "Character")
        self.assertEqual(get_pose()["bones"][0]["bone"], "head")
        rig_bone = get_rig()["bones"][0]
        self.assertEqual(rig_bone["semantic"], "head")
        self.assertTrue(rig_bone["has_ik_constraint"])
        self.assertEqual(len(rig_bone["rest"]["matrix_local"]), 4)

    def test_multiple_armatures_lists_names(self):
        make_armature("CharacterB")
        make_armature("CharacterA")
        with self.assertRaisesRegex(
            PoseBridgeError, r"\['CharacterA', 'CharacterB'\]"
        ):
            find_armature()

    def test_pose_edit_undo_and_reset(self):
        make_armature("Character")
        bpy.ops.ed.undo_push(message="Test fixture")
        result = set_bone_pose(
            {"bone": "head", "rotation_degrees": [0, 0, 15], "mode": "delta"}
        )
        self.assertEqual(result["undo_steps"], 1)
        self.assertGreater(
            abs(find_armature().pose.bones["head"].rotation_quaternion.z), 0.1
        )
        self.assertTrue(undo()["undone"])
        restored = find_armature().pose.bones["head"].rotation_quaternion
        self.assertAlmostEqual(abs(restored.w), 1.0, places=5)
        set_bone_pose(
            {"bone": "head", "rotation_degrees": [5, 0, 0], "mode": "absolute"}
        )
        self.assertEqual(reset_pose({"scope": "all"})["reset_bones"], 1)
        reset = find_armature().pose.bones["head"].rotation_quaternion
        self.assertAlmostEqual(abs(reset.w), 1.0, places=5)

suite = unittest.defaultTestLoader.loadTestsFromTestCase(BlenderBridgeTests)
result = unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():
    raise SystemExit(1)
