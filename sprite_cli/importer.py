from pathlib import Path

from PIL import Image


def import_image(image_path: Path, name: str | None = None) -> dict:
    """Convert a PNG image to a sprite JSON definition dict."""
    with Image.open(image_path) as source:
        img = source.convert("RGBA")
    width, height = img.size
    pixels = list(img.get_flattened_data())

    # Extract unique colors (ignoring transparent pixels)
    colors: dict[tuple[int, int, int], str] = {}
    for r, g, b, a in pixels:
        if a < 128:
            continue
        rgb = (r, g, b)
        if rgb not in colors:
            colors[rgb] = f"c{len(colors)}"

    # Build palette
    palette = {}
    for rgb, key in colors.items():
        palette[key] = f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"

    frame = []
    for y in range(height):
        row = []
        for x in range(width):
            r, g, b, a = pixels[(y * width) + x]
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
