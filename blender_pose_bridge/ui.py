import bpy
from bpy.props import PointerProperty, StringProperty

from .constants import HOST, PORT
from . import runtime


class POSEBRIDGE_PG_Settings(bpy.types.PropertyGroup):
    last_action: StringProperty(name="Last action", default="Automatically started")


class POSEBRIDGE_OT_Start(bpy.types.Operator):
    bl_idname = "pose_bridge.start"
    bl_label = "Start Pose Bridge"

    def execute(self, context):
        runtime.start()
        context.scene.pose_bridge_settings.last_action = "Start requested"
        return {"FINISHED"}


class POSEBRIDGE_OT_Stop(bpy.types.Operator):
    bl_idname = "pose_bridge.stop"
    bl_label = "Stop Pose Bridge"

    def execute(self, context):
        runtime.stop()
        context.scene.pose_bridge_settings.last_action = "Stopped"
        return {"FINISHED"}


class POSEBRIDGE_PT_Main(bpy.types.Panel):
    bl_label = "Blender Pose Bridge"
    bl_idname = "VIEW3D_PT_blender_pose_bridge"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Pose Bridge"

    def draw(self, context):
        layout = self.layout
        server = runtime.get_server()
        status = "Online" if server and server.online else "Offline"
        layout.label(text=f"Bridge: {status}")
        layout.label(text=f"{HOST}:{PORT}")
        if server and server.last_error:
            layout.label(text=server.last_error, icon="ERROR")
        row = layout.row(align=True)
        row.operator("pose_bridge.start", icon="PLAY")
        row.operator("pose_bridge.stop", icon="PAUSE")


CLASSES = (
    POSEBRIDGE_PG_Settings,
    POSEBRIDGE_OT_Start,
    POSEBRIDGE_OT_Stop,
    POSEBRIDGE_PT_Main,
)


def register_ui():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.pose_bridge_settings = PointerProperty(
        type=POSEBRIDGE_PG_Settings
    )


def unregister_ui():
    if hasattr(bpy.types.Scene, "pose_bridge_settings"):
        del bpy.types.Scene.pose_bridge_settings
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
