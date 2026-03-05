from PIL import Image
from sprite_cli.models import SpriteDefinition
from sprite_cli.renderer import render_frame


def test_render_simple_frame():
    sprite = SpriteDefinition.model_validate({
        "name": "test",
        "palette": {"r": "#FF0000", "g": "#00FF00"},
        "frames": {
            "idle": [
                [["r", "g"],
                 ["g", "r"]]
            ]
        }
    })
    img = render_frame(sprite, "idle", frame_index=0)
    assert isinstance(img, Image.Image)
    assert img.mode == "RGBA"
    assert img.getpixel((0, 0))[:3] == (255, 0, 0)


def test_render_transparent_pixels():
    sprite = SpriteDefinition.model_validate({
        "name": "test",
        "palette": {"r": "#FF0000"},
        "frames": {
            "idle": [
                [[None, "r"],
                 ["r", None]]
            ]
        }
    })
    img = render_frame(sprite, "idle", frame_index=0)
    assert img.getpixel((0, 0))[3] == 0


def test_render_with_size_scaling():
    sprite = SpriteDefinition.model_validate({
        "name": "test",
        "size": 32,
        "palette": {"r": "#FF0000"},
        "frames": {
            "idle": [
                [["r", "r"],
                 ["r", "r"]]
            ]
        }
    })
    img = render_frame(sprite, "idle", frame_index=0)
    assert img.size == (32, 32)


def test_render_hex_color_in_grid():
    sprite = SpriteDefinition.model_validate({
        "name": "test",
        "palette": {},
        "frames": {
            "idle": [
                [["#0000FF"]]
            ]
        }
    })
    img = render_frame(sprite, "idle", frame_index=0)
    assert img.getpixel((0, 0))[:3] == (0, 0, 255)
