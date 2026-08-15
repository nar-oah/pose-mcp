import bpy

from .errors import PoseBridgeError


def find_view3d_context():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type != "VIEW_3D":
                continue
            region = next((item for item in area.regions if item.type == "WINDOW"), None)
            if region:
                return window, area, region, area.spaces.active.region_3d
    raise PoseBridgeError("No active VIEW_3D window region is available for capture")


def save_view_state(region_3d):
    return {
        "view_distance": region_3d.view_distance,
        "view_location": region_3d.view_location.copy(),
        "view_rotation": region_3d.view_rotation.copy(),
        "view_perspective": region_3d.view_perspective,
    }


def restore_view(region_3d, state):
    for field, value in state.items():
        setattr(region_3d, field, value)
