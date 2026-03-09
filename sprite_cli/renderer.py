from functools import lru_cache

from PIL import Image

from sprite_cli.models import SpriteDefinition, Frame


@lru_cache(maxsize=512)
def _hex_to_rgba(hex_color: str) -> tuple[int, int, int, int]:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return (r, g, b, 255)


def resolve_color(pixel: str | None, palette: dict[str, str | None]) -> tuple[int, int, int, int]:
    if pixel is None:
        return (0, 0, 0, 0)
    if pixel.startswith("#"):
        return _hex_to_rgba(pixel)
    color = palette.get(pixel)
    if color is None:
        return (0, 0, 0, 0)
    return _hex_to_rgba(color)


def render_pixels(
    frame: Frame,
    palette: dict[str, str | None],
    size: int | None = None,
) -> Image.Image:
    grid_h = len(frame)
    grid_w = max((len(row) for row in frame), default=0)
    img = Image.new("RGBA", (grid_w, grid_h), (0, 0, 0, 0))

    if grid_w > 0 and grid_h > 0:
        pixels = [
            resolve_color(row[x] if x < len(row) else None, palette)
            for row in frame
            for x in range(grid_w)
        ]
        img.putdata(pixels)

    if size and grid_w > 0 and grid_h > 0:
        img = img.resize((size, size), Image.NEAREST)

    return img


def render_frame(
    sprite: SpriteDefinition,
    frame_name: str,
    frame_index: int = 0,
) -> Image.Image:
    frame = sprite.frames[frame_name][frame_index]
    return render_pixels(frame, sprite.palette, size=sprite.size)
