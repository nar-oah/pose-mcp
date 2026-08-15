# Blender Pose MCP operating rules

When using the `blender-pose` MCP to adjust a human pose:

1. Call `get_rig` and `get_pose` before editing.
2. Establish center of gravity with Root/pelvis/legs first.
3. Adjust spine and chest next.
4. Adjust shoulders and arms next.
5. Finish with neck, head, and hands.
6. Prefer `set_pose_batch` over many single-bone calls.
7. Call `get_viewport` after making changes.
8. Inspect the structured Pose data and every fixed view, then continue refining;
   do not assume one description is done.
9. Never call `save_blend` unless the user explicitly asks to save.

Use the real Blender bone names returned with the semantic labels. Use
`apply_smplx_pose` only for a full reset-and-import. Use `set_bone_pose` or
`set_pose_batch` for non-resetting interactive adjustments. Never modify the original
`reference/main.py` conversion rules to implement interactive delta rotations.
