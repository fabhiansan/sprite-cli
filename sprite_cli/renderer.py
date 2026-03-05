from PIL import Image

from sprite_cli.models import SpriteDefinition, Frame


def resolve_color(pixel: str | None, palette: dict[str, str | None]) -> tuple[int, int, int, int]:
    if pixel is None:
        return (0, 0, 0, 0)
    if pixel.startswith("#"):
        hex_color = pixel.lstrip("#")
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return (r, g, b, 255)
    color = palette.get(pixel)
    if color is None:
        return (0, 0, 0, 0)
    return resolve_color(color, {})


def render_frame(
    sprite: SpriteDefinition,
    frame_name: str,
    frame_index: int = 0,
) -> Image.Image:
    frame = sprite.frames[frame_name][frame_index]
    grid_h = len(frame)
    grid_w = max(len(row) for row in frame) if frame else 0

    img = Image.new("RGBA", (grid_w, grid_h), (0, 0, 0, 0))

    for y, row in enumerate(frame):
        for x, pixel in enumerate(row):
            color = resolve_color(pixel, sprite.palette)
            img.putpixel((x, y), color)

    if sprite.size and grid_w > 0 and grid_h > 0:
        img = img.resize((sprite.size, sprite.size), Image.NEAREST)

    return img
