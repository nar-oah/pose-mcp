from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

Vector3 = Annotated[list[FiniteFloat], Field(min_length=3, max_length=3)]
RotvecList = Annotated[list[Vector3], Field(max_length=128)]
RootPose = Annotated[list[Vector3], Field(min_length=1, max_length=1)]
RotationMode = Literal["absolute", "delta"]


class BoneChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bone: Annotated[str, Field(min_length=1)]
    rotation_degrees: Vector3
    mode: RotationMode = "absolute"


class SmplxPose(BaseModel):
    model_config = ConfigDict(extra="forbid")

    body_root_pose: RootPose | None = None
    body_pose: RotvecList | None = None
    lhand_pose: RotvecList | None = None
    rhand_pose: RotvecList | None = None
