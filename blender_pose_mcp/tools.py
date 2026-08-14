from typing import Annotated, Any

from mcp.server import MCPServer
from pydantic import Field

from .bridge_client import BridgeClient
from .models import (
    BoneChange, ResetScope, RootPose, RotationMode, RotvecList, SmplxPose,
    Vector3,
)

BatchChanges = Annotated[list[BoneChange], Field(min_length=1, max_length=256)]


def register_tools(mcp: MCPServer, bridge: BridgeClient) -> None:
    @mcp.tool()
    def ping() -> dict[str, Any]:
        """Test Codex -> MCP -> Blender and report file, version, and Armature."""
        return bridge.call("ping")

    @mcp.tool()
    def get_rig() -> dict[str, Any]:
        """Read the existing Armature hierarchy, rest basis, constraints, and roles."""
        return bridge.call("get_rig")

    @mcp.tool()
    def get_pose() -> dict[str, Any]:
        """Read all current local Pose Bone rotations in degrees and quaternions."""
        return bridge.call("get_pose")

    @mcp.tool()
    def set_bone_pose(
        bone: str,
        rotation_degrees: Vector3,
        mode: RotationMode = "absolute",
    ) -> dict[str, Any]:
        """Set or locally delta-rotate one Pose Bone without resetting other bones."""
        change = BoneChange(
            bone=bone, rotation_degrees=rotation_degrees, mode=mode
        )
        return bridge.call("set_bone_pose", change.model_dump())

    @mcp.tool()
    def set_pose_batch(changes: BatchChanges) -> dict[str, Any]:
        """Apply multiple local Pose Bone edits together as one Blender undo step."""
        params = {"changes": [change.model_dump() for change in changes]}
        return bridge.call("set_pose_batch", params)

    @mcp.tool()
    def apply_smplx_pose(
        body_root_pose: RootPose | None = None,
        body_pose: RotvecList | None = None,
        lhand_pose: RotvecList | None = None,
        rhand_pose: RotvecList | None = None,
    ) -> dict[str, Any]:
        """Reset then import one full SMPL-X pose using the verified main.py rules."""
        pose = SmplxPose(
            body_root_pose=body_root_pose,
            body_pose=body_pose,
            lhand_pose=lhand_pose,
            rhand_pose=rhand_pose,
        )
        return bridge.call("apply_smplx_pose", pose.model_dump(exclude_none=True))

    @mcp.tool()
    def reset_pose(scope: ResetScope = "all") -> dict[str, Any]:
        """Reset the existing Armature to its base pose. Only scope='all' is valid."""
        if scope != "all":
            raise ValueError("scope must be 'all'")
        return bridge.call("reset_pose", {"scope": scope})

    @mcp.tool()
    def undo() -> dict[str, Any]:
        """Use Blender's undo system to undo the most recent operation."""
        return bridge.call("undo")

    @mcp.tool()
    def get_viewport() -> dict[str, Any]:
        """Render the current VIEW_3D to a temporary PNG and return its local path."""
        return bridge.call("get_viewport")

    @mcp.tool()
    def save_blend() -> dict[str, Any]:
        """Save the current .blend; call only after an explicit user save request."""
        return bridge.call("save_blend")
