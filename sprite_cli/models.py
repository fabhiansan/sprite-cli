from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


PixelRow = list[str | None]
Frame = list[PixelRow]


class Transform(BaseModel):
    type: str
    x: int | None = None
    y: int | None = None
    angle: int | None = None
    axis: str | None = None
    factor: float | None = None
    from_color: str | None = None
    to_color: str | None = None


class Anchor(BaseModel):
    x: int
    y: int


class Region(BaseModel):
    x: int
    y: int
    w: int
    h: int

    @field_validator("w", "h")
    @classmethod
    def validate_extent(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("region width and height must be greater than 0")
        return value


class Animation(BaseModel):
    base: str
    transforms: list[list[Transform]] | list[Transform] = Field(default_factory=list)
    fps: int = 4
    loop: bool = True

    @field_validator("fps")
    @classmethod
    def validate_fps(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("fps must be greater than 0")
        return value


class SpriteDefinition(BaseModel):
    name: str
    size: int | None = None
    palette: dict[str, str | None]
    frames: dict[str, list[Frame]]
    animations: dict[str, Animation] = Field(default_factory=dict)
    anchors: dict[str, Anchor] = Field(default_factory=dict)
    regions: dict[str, Region] = Field(default_factory=dict)

    @field_validator("size")
    @classmethod
    def validate_size(cls, value: int | None) -> int | None:
        if value is not None and value <= 0:
            raise ValueError("size must be greater than 0")
        return value
