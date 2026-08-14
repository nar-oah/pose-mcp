bl_info = {
    "name": "Blender Pose Bridge",
    "author": "OpenAI",
    "version": (0, 1, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Pose Bridge",
    "description": "Local bridge for the dedicated Blender Pose MCP",
    "category": "Animation",
}

from . import runtime
from .ui import register_ui, unregister_ui


def register():
    register_ui()
    runtime.start()


def unregister():
    runtime.stop()
    unregister_ui()


if __name__ == "__main__":
    register()
