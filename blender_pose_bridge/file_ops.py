import os
import tempfile
import uuid

import bpy

from .armature import find_armature
from .errors import PoseBridgeError


def _view3d_context():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type != "VIEW_3D":
                continue
            region = next((item for item in area.regions if item.type == "WINDOW"), None)
            if region:
                return window, area, region
    raise PoseBridgeError("No active VIEW_3D window region is available for capture")


def get_viewport():
    armature = find_armature()
    window, area, region = _view3d_context()
    scene = bpy.context.scene
    filepath = os.path.join(
        tempfile.gettempdir(), f"blender_pose_viewport_{uuid.uuid4().hex}.png"
    )
    old_path = scene.render.filepath
    old_format = scene.render.image_settings.file_format
    old_extension = scene.render.use_file_extension
    try:
        scene.render.filepath = filepath
        scene.render.image_settings.file_format = "PNG"
        scene.render.use_file_extension = True
        with bpy.context.temp_override(
            window=window, screen=window.screen, area=area, region=region
        ):
            result = bpy.ops.render.opengl(write_still=True, view_context=True)
    finally:
        scene.render.filepath = old_path
        scene.render.image_settings.file_format = old_format
        scene.render.use_file_extension = old_extension
    if "FINISHED" not in result or not os.path.isfile(filepath):
        raise PoseBridgeError("Blender OpenGL viewport capture did not produce a PNG")
    return {
        "armature": armature.name,
        "path": filepath,
        "mime_type": "image/png",
        "size_bytes": os.path.getsize(filepath),
        "temporary": True,
    }


def save_blend():
    armature = find_armature()
    filepath = bpy.data.filepath
    if not filepath:
        raise PoseBridgeError(
            "The current project has no .blend path; save it once in Blender first"
        )
    result = bpy.ops.wm.save_as_mainfile(filepath=filepath, check_existing=False)
    if "FINISHED" not in result:
        raise PoseBridgeError("Blender could not save the current .blend")
    return {"saved": True, "blend_file": filepath, "armature": armature.name}
