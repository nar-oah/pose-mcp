import os
import tempfile
import uuid

import bpy
from mathutils import Vector

from .armature import find_armature
from .errors import PoseBridgeError
from .read_ops import get_pose

FIXED_VIEWS = (
    ("front", "FRONT"),
    ("left", "LEFT"),
    ("right", "RIGHT"),
    ("back", "BACK"),
)


def _view3d_context():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type != "VIEW_3D":
                continue
            region = next((item for item in area.regions if item.type == "WINDOW"), None)
            if region:
                return window, area, region, area.spaces.active.region_3d
    raise PoseBridgeError("No active VIEW_3D window region is available for capture")


def _belongs_to_rig(obj, armature):
    return obj == armature or obj.parent == armature or any(
        modifier.type == "ARMATURE" and modifier.object == armature
        for modifier in obj.modifiers
    )


def _frame(armature, region):
    points = [
        armature.matrix_world @ point
        for bone in armature.pose.bones
        for point in (bone.head, bone.tail)
    ]
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in bpy.context.scene.objects:
        if not _belongs_to_rig(obj, armature):
            continue
        evaluated = obj.evaluated_get(depsgraph)
        points.extend(
            evaluated.matrix_world @ Vector(corner) for corner in evaluated.bound_box
        )
    minimum = Vector(tuple(min(point[index] for point in points) for index in range(3)))
    maximum = Vector(tuple(max(point[index] for point in points) for index in range(3)))
    center = (minimum + maximum) / 2
    radius = max((point - center).length for point in points)
    aspect_margin = max(1.0, region.height / max(region.width, 1))
    return center, max(radius * 1.25 * aspect_margin, 0.25)


def _view_state(region_3d):
    return {
        "view_distance": region_3d.view_distance,
        "view_location": region_3d.view_location.copy(),
        "view_rotation": region_3d.view_rotation.copy(),
        "view_perspective": region_3d.view_perspective,
    }


def _restore_view(region_3d, state):
    for field, value in state.items():
        setattr(region_3d, field, value)


def _capture_view(context, center, distance, name, axis):
    window, area, region, region_3d = context
    filepath = os.path.join(
        tempfile.gettempdir(), f"blender_pose_{uuid.uuid4().hex}_{name}.png"
    )
    bpy.context.scene.render.filepath = filepath
    with bpy.context.temp_override(
        window=window, screen=window.screen, area=area, region=region
    ):
        bpy.ops.view3d.view_axis(type=axis, align_active=False)
        region_3d.view_location = center
        region_3d.view_distance = distance
        region_3d.view_perspective = "ORTHO"
        result = bpy.ops.render.opengl(write_still=True, view_context=True)
    if "FINISHED" not in result or not os.path.isfile(filepath):
        raise PoseBridgeError(f"Blender did not produce the fixed {name} view PNG")
    return {
        "name": name,
        "axis": axis,
        "projection": "orthographic",
        "path": filepath,
        "mime_type": "image/png",
        "size_bytes": os.path.getsize(filepath),
        "width": region.width,
        "height": region.height,
    }


def get_viewport():
    armature = find_armature()
    context = _view3d_context()
    region_3d = context[3]
    scene = bpy.context.scene
    center, distance = _frame(armature, context[2])
    old_view = _view_state(region_3d)
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
            _capture_view(context, center, distance, name, axis)
            for name, axis in FIXED_VIEWS
        ]
    finally:
        scene.render.filepath = old_render[0]
        scene.render.image_settings.file_format = old_render[1]
        scene.render.use_file_extension = old_render[2]
        _restore_view(region_3d, old_view)
    return {
        "armature": armature.name,
        "pose": get_pose(),
        "views": views,
        "temporary": True,
    }
