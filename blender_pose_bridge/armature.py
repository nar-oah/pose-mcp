import bpy

from .errors import PoseBridgeError


def find_armature():
    armatures = sorted(
        (obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE"),
        key=lambda obj: obj.name,
    )
    names = [obj.name for obj in armatures]
    if not armatures:
        raise PoseBridgeError("No Armature object exists in the current scene")
    if len(armatures) > 1:
        raise PoseBridgeError(
            f"Multiple Armature objects found; expected exactly one: {names}"
        )
    return armatures[0]


def pose_bone(armature, name):
    bone = armature.pose.bones.get(name)
    if bone is None:
        raise PoseBridgeError(
            f"Pose Bone '{name}' does not exist on Armature '{armature.name}'"
        )
    return bone
