from __future__ import annotations

from pydantic import BaseModel


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


class Animation(BaseModel):
    base: str
    transforms: list[list[Transform]] | list[Transform] = []
    fps: int = 4
    loop: bool = True


class SpriteDefinition(BaseModel):
    name: str
    size: int | None = None
    palette: dict[str, str | None]
    frames: dict[str, list[Frame]]
    animations: dict[str, Animation] = {}
