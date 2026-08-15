import bpy
from mathutils import Vector


def _belongs_to_rig(obj, armature):
    return obj == armature or obj.parent == armature or any(
        modifier.type == "ARMATURE" and modifier.object == armature
        for modifier in obj.modifiers
    )


def fit_frame(armature, region):
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
