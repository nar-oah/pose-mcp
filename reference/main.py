import bpy
import json
import math
from mathutils import Quaternion, Euler
from bpy.props import StringProperty, PointerProperty

bl_info = {
    "name": "SMPLest-X Loader (Simplified)",
    "author": "OpenAI",
    "version": (1, 4, 0),
    "location": "View3D > Sidebar > SMPLest-X",
    "description": "Simplified SMPL-X Pose Loader (Fixed to Retarget Mode)",
    "category": "Animation",
}

ROOT_BONE = "Root"
BODY_OFFSETS = {"upperarm_L": (0, 0, 30), "upperarm_R": (0, 0, -30)}
BODY_BONES = [
    "thigh_L",
    "thigh_R",
    "spine_01",
    "calf_L",
    "calf_R",
    "spine_02",
    "foot_L",
    "foot_R",
    "spine_03",
    "foot_sub_L",
    "foot_sub_R",
    "neck_01",
    "clavicle_L",
    "clavicle_R",
    "head",
    "upperarm_L",
    "upperarm_R",
    "lowerarm_L",
    "lowerarm_R",
    "hand_L",
    "hand_R",
]
FINGER_BONES = ["index", "middle", "pinky", "ring", "thumb"]
HAND_BONES = {
    "left": [f"{f}_0{i}_L" for f in FINGER_BONES for i in range(1, 4)],
    "right": [f"{f}_0{i}_R" for f in FINGER_BONES for i in range(1, 4)],
}


def rotvec_to_quaternion(rv):
    angle = math.sqrt(rv[0] ** 2 + rv[1] ** 2 + rv[2] ** 2)
    if angle < 1e-8:
        return Quaternion((1, 0, 0, 0))
    s = math.sin(angle / 2) / angle
    return Quaternion((math.cos(angle / 2), rv[0] * s, rv[1] * s, rv[2] * s))


def set_bone_rot(pb, rotvec, is_root=False, is_hand=False, offset_euler=None):
    pb.rotation_mode = "QUATERNION"
    rv = [-v for v in rotvec] if is_hand else rotvec
    q_data = rotvec_to_quaternion(rv)
    if offset_euler:
        q_offset = Euler([math.radians(a) for a in offset_euler], "XYZ").to_quaternion()
        q_data = q_offset @ q_data
    C = Quaternion((1.0, 0.0, 0.0), math.radians(90))
    q_armature = C @ q_data @ C.inverted()
    fix_q = Quaternion((1.0, 0.0, 0.0), math.radians(180))
    q_armature = fix_q @ q_armature if is_root else q_armature
    basis = pb.bone.matrix_local.to_quaternion()
    pb.rotation_quaternion = basis.inverted() @ q_armature @ basis


# --- 应用姿态 ---
def apply_pose(obj, data):
    pbones = obj.pose.bones
    # 重置姿态
    for pb in pbones:
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)

    # 处理 Root
    if "body_root_pose" in data:
        set_bone_rot(pbones[ROOT_BONE], data["body_root_pose"][0], is_root=True)

    # 处理 身体
    for name, rv in zip(BODY_BONES, data.get("body_pose", [])):
        if name in pbones:
            offset = BODY_OFFSETS.get(name, None)
            set_bone_rot(pbones[name], rv, offset_euler=offset)

    # 处理 手部
    for side in ["left", "right"]:
        pose_key = f"{side[0]}hand_pose"
        for name, rv in zip(HAND_BONES[side], data.get(pose_key, [])):
            if name in pbones:
                set_bone_rot(pbones[name], rv, is_hand=True)

    bpy.context.view_layer.update()


# --- UI & Operator ---
class OT_ApplySMPLX(bpy.types.Operator):
    bl_idname = "object.apply_smplx_simple"
    bl_label = "Apply Pose"

    def execute(self, context):
        set = context.scene.smplx_tool
        if not set.armature or not set.path:
            self.report({"ERROR"}, "Missing Path or Armature")
            return {"CANCELLED"}

        with open(bpy.path.abspath(set.path), "r") as f:
            data = json.load(f)

        apply_pose(set.armature, data)
        return {"FINISHED"}


class SMPLX_Panel(bpy.types.Panel):
    bl_label = "SMPL-X Loader"
    bl_idname = "VIEW3D_PT_smplx_simple"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SMPLest-X"

    def draw(self, context):
        layout = self.layout
        tool = context.scene.smplx_tool
        layout.prop(tool, "path", text="JSON")
        layout.prop(tool, "armature", text="Target")
        layout.operator("object.apply_smplx_simple", icon="ANIM")


class SMPLX_Settings(bpy.types.PropertyGroup):
    path: StringProperty(name="Path", subtype="FILE_PATH")
    armature: PointerProperty(name="Armature", type=bpy.types.Object)


classes = (SMPLX_Settings, OT_ApplySMPLX, SMPLX_Panel)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.smplx_tool = PointerProperty(type=SMPLX_Settings)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.smplx_tool


if __name__ == "__main__":
    register()
