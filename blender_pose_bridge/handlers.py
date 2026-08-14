from .file_ops import get_viewport, save_blend
from .pose_ops import reset_pose, set_bone_pose, set_pose_batch
from .read_ops import get_pose, get_rig, ping
from .smplx import apply_smplx_pose
from .undo_ops import undo

HANDLERS = {
    "ping": lambda _params: ping(),
    "get_rig": lambda _params: get_rig(),
    "get_pose": lambda _params: get_pose(),
    "set_bone_pose": set_bone_pose,
    "set_pose_batch": set_pose_batch,
    "apply_smplx_pose": apply_smplx_pose,
    "reset_pose": reset_pose,
    "undo": lambda _params: undo(),
    "get_viewport": lambda _params: get_viewport(),
    "save_blend": lambda _params: save_blend(),
}


def dispatch(method, params):
    if method not in HANDLERS:
        raise ValueError(f"Unsupported Blender Pose Bridge method: {method}")
    if not isinstance(params, dict):
        raise ValueError("Bridge params must be a JSON object")
    return HANDLERS[method](params)
