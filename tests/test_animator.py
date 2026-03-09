import tempfile
from pathlib import Path

from PIL import Image

from sprite_cli.models import SpriteDefinition
from sprite_cli.animator import create_animation, create_sprite_sheet


def _make_sprite():
    return SpriteDefinition.model_validate({
        "name": "test",
        "palette": {"r": "#FF0000", "g": "#00FF00"},
        "frames": {
            "walk": [
                [["r", "g"], ["g", "r"]],
                [["g", "r"], ["r", "g"]],
            ]
        },
        "animations": {
            "bounce": {
                "base": "walk",
                "transforms": [
                    [{"type": "translate", "y": -1}],
                    [{"type": "translate", "y": 0}],
                ],
                "fps": 4,
            }
        }
    })


def test_create_animation_from_frames():
    sprite = _make_sprite()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test.gif"
        create_animation(sprite, frame_name="walk", output_path=out, fps=4)
        assert out.exists()
        img = Image.open(out)
        assert img.format == "GIF"
        assert img.n_frames == 2


def test_create_animation_from_transforms():
    sprite = _make_sprite()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test.gif"
        create_animation(sprite, animation_name="bounce", output_path=out)
        assert out.exists()
        img = Image.open(out)
        assert img.format == "GIF"
        assert img.n_frames == 2


def test_create_animation_respects_loop_flag():
    sprite = SpriteDefinition.model_validate({
        "name": "test",
        "palette": {"r": "#FF0000"},
        "frames": {"idle": [[["r"]]]},
        "animations": {
            "once": {
                "base": "idle",
                "transforms": [[{"type": "translate", "y": 0}]],
                "loop": False,
            }
        },
    })

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "once.gif"
        create_animation(sprite, animation_name="once", output_path=out)
        img = Image.open(out)
        assert img.info["loop"] == 1


def test_create_sprite_sheet():
    sprite = _make_sprite()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "sheet.png"
        create_sprite_sheet(sprite, frame_name="walk", output_path=out)
        assert out.exists()
        img = Image.open(out)
        assert img.size == (4, 2)
