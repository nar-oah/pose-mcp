HOST = "127.0.0.1"
PORT = 8766
ROOT_BONE = "Root"
BODY_OFFSETS = {"upperarm_L": (0, 0, 30), "upperarm_R": (0, 0, -30)}
BODY_BONES = [
    "thigh_L", "thigh_R", "spine_01", "calf_L", "calf_R", "spine_02",
    "foot_L", "foot_R", "spine_03", "foot_sub_L", "foot_sub_R",
    "neck_01", "clavicle_L", "clavicle_R", "head", "upperarm_L",
    "upperarm_R", "lowerarm_L", "lowerarm_R", "hand_L", "hand_R",
]
FINGER_BONES = ["index", "middle", "pinky", "ring", "thumb"]
HAND_BONES = {
    "left": [f"{finger}_0{i}_L" for finger in FINGER_BONES for i in range(1, 4)],
    "right": [f"{finger}_0{i}_R" for finger in FINGER_BONES for i in range(1, 4)],
}
SEMANTIC_BONES = {
    "Root": "hips/root",
    "thigh_L": "left thigh", "thigh_R": "right thigh",
    "calf_L": "left calf", "calf_R": "right calf",
    "foot_L": "left foot", "foot_R": "right foot",
    "foot_sub_L": "left toe", "foot_sub_R": "right toe",
    "spine_01": "lower spine", "spine_02": "middle spine",
    "spine_03": "upper spine", "neck_01": "neck", "head": "head",
    "clavicle_L": "left clavicle", "clavicle_R": "right clavicle",
    "upperarm_L": "left upper arm", "upperarm_R": "right upper arm",
    "lowerarm_L": "left forearm", "lowerarm_R": "right forearm",
    "hand_L": "left hand", "hand_R": "right hand",
}


def semantic_name(name):
    if name in SEMANTIC_BONES:
        return SEMANTIC_BONES[name]
    for side, suffix in (("left", "_L"), ("right", "_R")):
        if name in HAND_BONES[side]:
            stem, segment, _ = name.rsplit("_", 2)
            return f"{side} {stem} {int(segment)}"
    return None


def bone_groups(name):
    groups = []
    if name == ROOT_BONE:
        groups.append("ROOT")
    if name in BODY_BONES:
        groups.append("BODY_BONES")
    if any(name in bones for bones in HAND_BONES.values()):
        groups.append("HAND_BONES")
    return groups
