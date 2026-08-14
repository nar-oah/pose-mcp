"""Open this file in Blender's Text Editor and choose Run Script.

WARNING: the final step resets the current Armature pose. The file is not saved.
"""

import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from blender_pose_bridge.handlers import dispatch


def show(step, result):
    print(f"[{step}] {json.dumps(result, ensure_ascii=False)[:1000]}")


show("1 ping", dispatch("ping", {}))
show("2 get_rig", dispatch("get_rig", {}))
show("3 get_pose", dispatch("get_pose", {}))
show(
    "4 modify head",
    dispatch(
        "set_bone_pose",
        {"bone": "head", "rotation_degrees": [0, 0, 5], "mode": "delta"},
    ),
)
show("5 undo", dispatch("undo", {}))
show("6 reset", dispatch("reset_pose", {"scope": "all"}))
print("Smoke test complete. The .blend was not saved.")
