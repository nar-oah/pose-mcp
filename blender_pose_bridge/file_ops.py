import bpy

from .armature import find_armature
from .errors import PoseBridgeError
from .viewport import get_viewport


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
