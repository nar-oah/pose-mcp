SERVER_INSTRUCTIONS = """This server only poses the one existing Blender Armature.
Start by calling get_rig and get_pose. Establish balance with root/pelvis/legs, then
spine/chest, shoulders/arms, and finally neck/head/hands. Prefer set_pose_batch.
After edits call get_viewport, compare its structured joint data and all four fixed
views, then continue refining; one natural language request does not imply the pose
is finished. Never call save_blend unless the user explicitly asks to save.
apply_smplx_pose is a full reset-and-import path;
set_bone_pose and set_pose_batch are non-resetting local-pose edits. The bridge
cannot edit rest pose, bones, meshes, weights, materials, or execute Python.
"""
