import importlib.util
import os
import sys
import unittest

import bpy

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from blender_pose_bridge.smplx import set_bone_rot

REFERENCE_PATH = os.path.join(REPO_ROOT, "reference", "main.py")
SPEC = importlib.util.spec_from_file_location("verified_pose_reference", REFERENCE_PATH)
REFERENCE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REFERENCE)


def make_bone_pair():
    data = bpy.data.armatures.new("CharacterData")
    armature = bpy.data.objects.new("Character", data)
    bpy.context.scene.collection.objects.link(armature)
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    for name in ("ours", "reference"):
        bone = data.edit_bones.new(name)
        bone.tail = (0, 0, 1)
    bpy.ops.object.mode_set(mode="OBJECT")
    return armature.pose.bones["ours"], armature.pose.bones["reference"]


class SmplxConversionTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def test_conversion_matches_verified_main(self):
        ours, reference = make_bone_pair()
        cases = (
            ({"is_root": True}, [0.2, -0.1, 0.3]),
            ({"is_hand": True}, [0.1, 0.2, -0.2]),
            ({"offset_euler": (0, 0, 30)}, [-0.3, 0.1, 0.2]),
        )
        for options, rotvec in cases:
            set_bone_rot(ours, rotvec, **options)
            REFERENCE.set_bone_rot(reference, rotvec, **options)
            difference = ours.rotation_quaternion.rotation_difference(
                reference.rotation_quaternion
            )
            self.assertAlmostEqual(difference.angle, 0.0, places=6)


suite = unittest.defaultTestLoader.loadTestsFromTestCase(SmplxConversionTests)
result = unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():
    raise SystemExit(1)
