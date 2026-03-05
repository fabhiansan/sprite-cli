import json
from pathlib import Path

from PIL import Image


def import_image(image_path: Path, name: str | None = None) -> dict:
    """Convert a PNG image to a sprite JSON definition dict."""
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size

    # Extract unique colors (ignoring transparent pixels)
    colors: dict[tuple[int, int, int], str] = {}
    color_index = 0

    # First pass: collect unique colors
    for y in range(height):
        for x in range(width):
            r, g, b, a = img.getpixel((x, y))
            if a < 128:
                continue
            rgb = (r, g, b)
            if rgb not in colors:
                colors[rgb] = f"c{color_index}"
                color_index += 1

    # Build palette
    palette = {}
    for rgb, key in colors.items():
        palette[key] = f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"

    # Second pass: build pixel grid
    frame = []
    for y in range(height):
        row = []
        for x in range(width):
            r, g, b, a = img.getpixel((x, y))
            if a < 128:
                row.append(None)
            else:
                row.append(colors[(r, g, b)])
        frame.append(row)

    sprite_name = name or Path(image_path).stem

    return {
        "name": sprite_name,
        "palette": palette,
        "frames": {
            "idle": [frame]
        },
        "animations": {}
    }
