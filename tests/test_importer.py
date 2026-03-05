import json
import tempfile
from pathlib import Path

from PIL import Image

from sprite_cli.importer import import_image
from sprite_cli.models import SpriteDefinition


def test_import_simple_image():
    img = Image.new("RGBA", (3, 2), (0, 0, 0, 0))
    img.putpixel((0, 0), (255, 0, 0, 255))
    img.putpixel((1, 0), (0, 255, 0, 255))
    img.putpixel((2, 0), (255, 0, 0, 255))
    img.putpixel((0, 1), (0, 255, 0, 255))
    img.putpixel((1, 1), (255, 0, 0, 255))
    img.putpixel((2, 1), (0, 0, 0, 0))  # transparent

    with tempfile.TemporaryDirectory() as tmp:
        png_path = Path(tmp) / "test.png"
        img.save(png_path)

        sprite_data = import_image(png_path, name="test")

    assert sprite_data["name"] == "test"
    # Should have 2 colors in palette (red and green)
    assert len(sprite_data["palette"]) == 2
    # Should have one frame set "idle" with one frame
    assert "idle" in sprite_data["frames"]
    assert len(sprite_data["frames"]["idle"]) == 1
    frame = sprite_data["frames"]["idle"][0]
    assert len(frame) == 2  # 2 rows
    assert len(frame[0]) == 3  # 3 columns
    # Last pixel of second row should be None (transparent)
    assert frame[1][2] is None
    # Should be valid as a SpriteDefinition
    SpriteDefinition.model_validate(sprite_data)


def test_import_fully_transparent():
    img = Image.new("RGBA", (2, 2), (0, 0, 0, 0))

    with tempfile.TemporaryDirectory() as tmp:
        png_path = Path(tmp) / "empty.png"
        img.save(png_path)

        sprite_data = import_image(png_path, name="empty")

    assert sprite_data["palette"] == {}
    frame = sprite_data["frames"]["idle"][0]
    assert all(pixel is None for row in frame for pixel in row)


def test_import_preserves_colors():
    img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    img.putpixel((0, 0), (100, 150, 200, 255))

    with tempfile.TemporaryDirectory() as tmp:
        png_path = Path(tmp) / "color.png"
        img.save(png_path)

        sprite_data = import_image(png_path, name="color")

    # The palette should have the exact hex color
    palette_values = list(sprite_data["palette"].values())
    assert len(palette_values) == 1
    assert palette_values[0].upper() == "#6496C8"


def test_import_roundtrip():
    """Import a rendered sprite and verify it produces a valid definition."""
    from sprite_cli.renderer import render_frame

    original = SpriteDefinition.model_validate({
        "name": "roundtrip",
        "palette": {"r": "#FF0000", "g": "#00FF00"},
        "frames": {
            "idle": [
                [["r", "g", None],
                 [None, "r", "g"]]
            ]
        }
    })
    img = render_frame(original, "idle", frame_index=0)

    with tempfile.TemporaryDirectory() as tmp:
        png_path = Path(tmp) / "rt.png"
        img.save(png_path)

        imported = import_image(png_path, name="roundtrip")

    sprite = SpriteDefinition.model_validate(imported)
    assert len(sprite.palette) == 2
    frame = sprite.frames["idle"][0]
    # Top-right should be None (transparent)
    assert frame[0][2] is None
    # Bottom-left should be None
    assert frame[1][0] is None
