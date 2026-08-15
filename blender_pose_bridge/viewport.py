import os
import tempfile
import uuid

import bpy
from mathutils import Quaternion

from .armature import find_armature
from .errors import PoseBridgeError
from .read_ops import get_pose
from .viewport_context import find_view3d_context, restore_view, save_view_state
from .viewport_frame import fit_frame

FIXED_VIEWS = (
    ("front", "FRONT", (0.707107, 0.707107, 0.0, 0.0)),
    ("left", "LEFT", (0.5, 0.5, -0.5, -0.5)),
    ("right", "RIGHT", (0.5, 0.5, 0.5, 0.5)),
    ("back", "BACK", (0.0, 0.0, 0.707107, 0.707107)),
)
MAX_VIEW_HEIGHT = 768


def _normalize_image(filepath):
    image = bpy.data.images.load(filepath, check_existing=False)
    try:
        width, height = image.size
        if height > MAX_VIEW_HEIGHT:
            width = round(width * MAX_VIEW_HEIGHT / height)
            height = MAX_VIEW_HEIGHT
            image.scale(width, height)
            image.filepath_raw = filepath
            image.file_format = "PNG"
            image.save()
        return int(width), int(height)
    finally:
        bpy.data.images.remove(image)


def _capture_view(context, center, distance, name, axis, rotation):
    window, area, region, region_3d = context
    filepath = os.path.join(
        tempfile.gettempdir(), f"blender_pose_{uuid.uuid4().hex}_{name}.png"
    )
    bpy.context.scene.render.filepath = filepath
    with bpy.context.temp_override(
        window=window, screen=window.screen, area=area, region=region
    ):
        region_3d.view_rotation = Quaternion(rotation)
        region_3d.view_location = center
        region_3d.view_distance = distance
        region_3d.view_perspective = "ORTHO"
        result = bpy.ops.render.opengl(write_still=True, view_context=True)
    if "FINISHED" not in result or not os.path.isfile(filepath):
        raise PoseBridgeError(f"Blender did not produce the fixed {name} view PNG")
    width, height = _normalize_image(filepath)
    return {
        "name": name,
        "axis": axis,
        "view_rotation": list(rotation),
        "projection": "orthographic",
        "path": filepath,
        "mime_type": "image/png",
        "size_bytes": os.path.getsize(filepath),
        "width": width,
        "height": height,
    }


def get_viewport():
    armature = find_armature()
    context = find_view3d_context()
    region_3d = context[3]
    scene = bpy.context.scene
    center, distance = fit_frame(armature, context[2])
    old_view = save_view_state(region_3d)
    old_render = (
        scene.render.filepath,
        scene.render.image_settings.file_format,
        scene.render.use_file_extension,
    )
    views = []
    try:
        scene.render.image_settings.file_format = "PNG"
        scene.render.use_file_extension = True
        views = [
            _capture_view(context, center, distance, name, axis, rotation)
            for name, axis, rotation in FIXED_VIEWS
        ]
    finally:
        scene.render.filepath = old_render[0]
        scene.render.image_settings.file_format = old_render[1]
        scene.render.use_file_extension = old_render[2]
        restore_view(region_3d, old_view)
    return {
        "armature": armature.name,
        "pose": get_pose(),
        "views": views,
        "temporary": True,
    }
