# Sprite CLI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python CLI that renders pixel-art sprites from JSON definitions — PNG, animated GIF, and sprite sheets.

**Architecture:** JSON sprite definitions are parsed into Pydantic models, rendered with Pillow, and exposed via Click CLI commands. Transforms (translate, rotate, flip, scale, recolor) generate animation frames from a base frame.

**Tech Stack:** Python 3.10+, Click, Pillow, Pydantic

---

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `sprite_cli/__init__.py`
- Create: `sprite_cli/cli.py`

**Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "sprite-cli"
version = "0.1.0"
description = "Pixel-art sprite CLI for AI-driven game asset creation"
requires-python = ">=3.10"
dependencies = [
    "click>=8.0",
    "pillow>=10.0",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.0"]

[project.scripts]
sprite = "sprite_cli.cli:cli"
```

**Step 2: Create sprite_cli/__init__.py**

```python
"""Sprite CLI - pixel-art sprite generator."""
```

**Step 3: Create minimal cli.py**

```python
import click


@click.group()
def cli():
    """Pixel-art sprite CLI."""
    pass


if __name__ == "__main__":
    cli()
```

**Step 4: Install in dev mode and verify**

Run: `pip install -e ".[dev]"`
Then: `sprite --help`
Expected: Shows help text with "Pixel-art sprite CLI."

**Step 5: Init git and commit**

```bash
git init
git add pyproject.toml sprite_cli/__init__.py sprite_cli/cli.py
git commit -m "feat: project scaffolding with Click CLI entry point"
```

---

### Task 2: Pydantic Models

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_models.py`
- Create: `sprite_cli/models.py`

**Step 1: Write the failing test**

```python
import pytest
from sprite_cli.models import SpriteDefinition


def test_parse_minimal_sprite():
    data = {
        "name": "test",
        "palette": {"body": "#FF0000"},
        "frames": {
            "idle": [
                [["body", "body"],
                 ["body", "body"]]
            ]
        }
    }
    sprite = SpriteDefinition.model_validate(data)
    assert sprite.name == "test"
    assert sprite.palette == {"body": "#FF0000"}
    assert len(sprite.frames["idle"]) == 1
    assert sprite.size is None
    assert sprite.animations == {}


def test_parse_sprite_with_animation():
    data = {
        "name": "robot",
        "size": 32,
        "palette": {"body": "#4A90D9", "eye": "#FFFFFF"},
        "frames": {
            "idle": [
                [[None, "body", None],
                 ["body", "eye", "body"],
                 ["body", "body", "body"]]
            ]
        },
        "animations": {
            "bounce": {
                "base": "idle",
                "transforms": [
                    [{"type": "translate", "y": -2}],
                    [{"type": "translate", "y": 0}]
                ],
                "fps": 4
            }
        }
    }
    sprite = SpriteDefinition.model_validate(data)
    assert sprite.size == 32
    assert sprite.animations["bounce"].base == "idle"
    assert sprite.animations["bounce"].fps == 4
    assert len(sprite.animations["bounce"].transforms) == 2


def test_parse_sprite_with_hex_colors_in_grid():
    data = {
        "name": "direct",
        "palette": {},
        "frames": {
            "idle": [
                [["#FF0000", "#00FF00"],
                 ["#0000FF", None]]
            ]
        }
    }
    sprite = SpriteDefinition.model_validate(data)
    assert sprite.frames["idle"][0][0][0] == "#FF0000"
    assert sprite.frames["idle"][0][1][1] is None


def test_invalid_sprite_missing_name():
    with pytest.raises(Exception):
        SpriteDefinition.model_validate({"palette": {}, "frames": {}})
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_models.py -v`
Expected: FAIL — cannot import SpriteDefinition

**Step 3: Write the models**

```python
from __future__ import annotations

from pydantic import BaseModel


# A pixel row is a list of color keys (palette references), hex strings, or None (transparent)
PixelRow = list[str | None]
# A frame is a 2D grid of pixel rows
Frame = list[PixelRow]


class Transform(BaseModel):
    type: str  # translate, rotate, flip, scale, recolor
    x: int | None = None
    y: int | None = None
    angle: int | None = None
    axis: str | None = None
    factor: float | None = None
    from_color: str | None = None
    to_color: str | None = None

    class Config:
        populate_by_name = True

    def model_post_init(self, __context):
        # Support "from" and "to" as JSON keys (reserved words in Python)
        pass


class Animation(BaseModel):
    base: str  # name of a frame set in frames dict
    transforms: list[list[Transform]] | list[Transform] = []
    fps: int = 4
    loop: bool = True


class SpriteDefinition(BaseModel):
    name: str
    size: int | None = None
    palette: dict[str, str | None]
    frames: dict[str, list[Frame]]  # name -> list of frames (each frame is a 2D grid)
    animations: dict[str, Animation] = {}
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_models.py -v`
Expected: All 4 tests PASS

**Step 5: Commit**

```bash
git add tests/ sprite_cli/models.py
git commit -m "feat: add Pydantic models for sprite definitions"
```

---

### Task 3: Renderer (JSON to PNG)

**Files:**
- Create: `tests/test_renderer.py`
- Create: `sprite_cli/renderer.py`

**Step 1: Write the failing test**

```python
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
    # Each pixel scaled up — check the top-left pixel color
    assert img.getpixel((0, 0))[:3] == (255, 0, 0)  # red


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
    # Top-left should be transparent
    assert img.getpixel((0, 0))[3] == 0  # alpha = 0


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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_renderer.py -v`
Expected: FAIL — cannot import render_frame

**Step 3: Write the renderer**

```python
from PIL import Image

from sprite_cli.models import SpriteDefinition, Frame


def resolve_color(pixel: str | None, palette: dict[str, str | None]) -> tuple[int, int, int, int]:
    """Resolve a pixel value to an RGBA tuple."""
    if pixel is None:
        return (0, 0, 0, 0)
    # Check if it's a hex color
    if pixel.startswith("#"):
        hex_color = pixel.lstrip("#")
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return (r, g, b, 255)
    # Otherwise it's a palette key
    color = palette.get(pixel)
    if color is None:
        return (0, 0, 0, 0)
    return resolve_color(color, {})


def render_frame(
    sprite: SpriteDefinition,
    frame_name: str,
    frame_index: int = 0,
) -> Image.Image:
    """Render a single frame to a Pillow Image."""
    frame = sprite.frames[frame_name][frame_index]
    grid_h = len(frame)
    grid_w = max(len(row) for row in frame) if frame else 0

    # Create 1:1 pixel image first
    img = Image.new("RGBA", (grid_w, grid_h), (0, 0, 0, 0))

    for y, row in enumerate(frame):
        for x, pixel in enumerate(row):
            color = resolve_color(pixel, sprite.palette)
            img.putpixel((x, y), color)

    # Scale to target size if specified
    if sprite.size and grid_w > 0 and grid_h > 0:
        img = img.resize((sprite.size, sprite.size), Image.NEAREST)

    return img
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_renderer.py -v`
Expected: All 4 tests PASS

**Step 5: Commit**

```bash
git add tests/test_renderer.py sprite_cli/renderer.py
git commit -m "feat: add renderer to convert sprite frames to PNG"
```

---

### Task 4: Transforms

**Files:**
- Create: `tests/test_transforms.py`
- Create: `sprite_cli/transforms.py`

**Step 1: Write the failing tests**

```python
from sprite_cli.models import Frame, Transform
from sprite_cli.transforms import apply_transform


def test_translate():
    frame: Frame = [
        [None, None, None],
        [None, "r", None],
        [None, None, None],
    ]
    t = Transform(type="translate", x=1, y=0)
    result = apply_transform(frame, t)
    assert result[1][2] == "r"
    assert result[1][1] is None


def test_translate_up():
    frame: Frame = [
        [None, None, None],
        [None, "r", None],
        [None, None, None],
    ]
    t = Transform(type="translate", x=0, y=-1)
    result = apply_transform(frame, t)
    assert result[0][1] == "r"
    assert result[1][1] is None


def test_flip_horizontal():
    frame: Frame = [
        ["r", "g"],
        ["b", "w"],
    ]
    t = Transform(type="flip", axis="horizontal")
    result = apply_transform(frame, t)
    assert result == [["g", "r"], ["w", "b"]]


def test_flip_vertical():
    frame: Frame = [
        ["r", "g"],
        ["b", "w"],
    ]
    t = Transform(type="flip", axis="vertical")
    result = apply_transform(frame, t)
    assert result == [["b", "w"], ["r", "g"]]


def test_rotate_90():
    frame: Frame = [
        ["r", "g"],
        ["b", "w"],
    ]
    t = Transform(type="rotate", angle=90)
    result = apply_transform(frame, t)
    assert result == [["b", "r"], ["w", "g"]]


def test_recolor():
    frame: Frame = [
        ["r", "g"],
        ["r", "b"],
    ]
    t = Transform(type="recolor", from_color="r", to_color="g")
    result = apply_transform(frame, t)
    assert result == [["g", "g"], ["g", "b"]]


def test_scale():
    frame: Frame = [
        ["r", "g"],
        ["b", "w"],
    ]
    t = Transform(type="scale", factor=2.0)
    result = apply_transform(frame, t)
    assert len(result) == 4
    assert len(result[0]) == 4
    assert result[0][0] == "r"
    assert result[0][1] == "r"
    assert result[1][0] == "r"
    assert result[1][1] == "r"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_transforms.py -v`
Expected: FAIL — cannot import apply_transform

**Step 3: Write the transforms module**

```python
import copy
from sprite_cli.models import Frame, Transform


def apply_transform(frame: Frame, transform: Transform) -> Frame:
    """Apply a single transform to a frame, returning a new frame."""
    if transform.type == "translate":
        return _translate(frame, transform.x or 0, transform.y or 0)
    elif transform.type == "flip":
        return _flip(frame, transform.axis or "horizontal")
    elif transform.type == "rotate":
        return _rotate(frame, transform.angle or 90)
    elif transform.type == "recolor":
        return _recolor(frame, transform.from_color or "", transform.to_color or "")
    elif transform.type == "scale":
        return _scale(frame, transform.factor or 1.0)
    else:
        raise ValueError(f"Unknown transform type: {transform.type}")


def _translate(frame: Frame, dx: int, dy: int) -> Frame:
    h = len(frame)
    w = max(len(row) for row in frame) if frame else 0
    new_frame: Frame = [[None] * w for _ in range(h)]
    for y, row in enumerate(frame):
        for x, pixel in enumerate(row):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                new_frame[ny][nx] = pixel
    return new_frame


def _flip(frame: Frame, axis: str) -> Frame:
    if axis == "horizontal":
        return [list(reversed(row)) for row in frame]
    else:  # vertical
        return list(reversed([list(row) for row in frame]))


def _rotate(frame: Frame, angle: int) -> Frame:
    h = len(frame)
    w = max(len(row) for row in frame) if frame else 0
    steps = (angle // 90) % 4
    result = [list(row) for row in frame]
    for _ in range(steps):
        rh = len(result)
        rw = max(len(row) for row in result) if result else 0
        rotated: Frame = [[None] * rh for _ in range(rw)]
        for y in range(rh):
            for x in range(len(result[y])):
                rotated[x][rh - 1 - y] = result[y][x]
        result = rotated
    return result


def _recolor(frame: Frame, from_color: str, to_color: str) -> Frame:
    return [
        [to_color if pixel == from_color else pixel for pixel in row]
        for row in frame
    ]


def _scale(frame: Frame, factor: float) -> Frame:
    h = len(frame)
    w = max(len(row) for row in frame) if frame else 0
    new_h = int(h * factor)
    new_w = int(w * factor)
    new_frame: Frame = [[None] * new_w for _ in range(new_h)]
    for ny in range(new_h):
        for nx in range(new_w):
            oy = int(ny / factor)
            ox = int(nx / factor)
            oy = min(oy, h - 1)
            ox = min(ox, w - 1)
            new_frame[ny][nx] = frame[oy][ox] if ox < len(frame[oy]) else None
    return new_frame
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_transforms.py -v`
Expected: All 7 tests PASS

**Step 5: Commit**

```bash
git add tests/test_transforms.py sprite_cli/transforms.py
git commit -m "feat: add transform system (translate, flip, rotate, recolor, scale)"
```

---

### Task 5: Animator (GIF + Sprite Sheets)

**Files:**
- Create: `tests/test_animator.py`
- Create: `sprite_cli/animator.py`

**Step 1: Write the failing tests**

```python
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


def test_create_sprite_sheet():
    sprite = _make_sprite()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "sheet.png"
        create_sprite_sheet(sprite, frame_name="walk", output_path=out)
        assert out.exists()
        img = Image.open(out)
        # 2 frames side by side: width = 2 * 2 = 4, height = 2
        assert img.size == (4, 2)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_animator.py -v`
Expected: FAIL — cannot import from animator

**Step 3: Write the animator**

```python
from pathlib import Path

from PIL import Image

from sprite_cli.models import SpriteDefinition, Transform
from sprite_cli.renderer import render_frame
from sprite_cli.transforms import apply_transform


def _generate_transform_frames(
    sprite: SpriteDefinition,
    animation_name: str,
) -> list[Image.Image]:
    """Generate frames by applying transforms to a base frame."""
    anim = sprite.animations[animation_name]
    base_frame = sprite.frames[anim.base][0]  # first frame of the base
    images = []

    for transform_step in anim.transforms:
        # Each step can be a single transform or list of transforms
        if isinstance(transform_step, list):
            transforms = transform_step
        else:
            transforms = [transform_step]

        frame = [list(row) for row in base_frame]
        for t in transforms:
            frame = apply_transform(frame, t)

        # Build a temporary sprite to render this frame
        temp = sprite.model_copy(update={
            "frames": {**sprite.frames, "__temp__": [frame]}
        })
        img = render_frame(temp, "__temp__", frame_index=0)
        images.append(img)

    return images


def create_animation(
    sprite: SpriteDefinition,
    output_path: Path,
    frame_name: str | None = None,
    animation_name: str | None = None,
    fps: int | None = None,
) -> None:
    """Create an animated GIF from frame-by-frame or transform-based animation."""
    if animation_name and animation_name in sprite.animations:
        images = _generate_transform_frames(sprite, animation_name)
        fps = fps or sprite.animations[animation_name].fps
    elif frame_name and frame_name in sprite.frames:
        images = [
            render_frame(sprite, frame_name, i)
            for i in range(len(sprite.frames[frame_name]))
        ]
        fps = fps or 4
    else:
        raise ValueError("Must specify either frame_name or animation_name")

    if not images:
        raise ValueError("No frames to animate")

    fps = fps or 4
    duration = int(1000 / fps)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=0,
        disposal=2,
    )


def create_sprite_sheet(
    sprite: SpriteDefinition,
    frame_name: str,
    output_path: Path,
    columns: int | None = None,
) -> None:
    """Create a sprite sheet PNG with all frames arranged in a grid."""
    frames = [
        render_frame(sprite, frame_name, i)
        for i in range(len(sprite.frames[frame_name]))
    ]

    if not frames:
        raise ValueError("No frames to create sheet from")

    frame_w, frame_h = frames[0].size
    n = len(frames)
    cols = columns or n
    rows = (n + cols - 1) // cols

    sheet = Image.new("RGBA", (cols * frame_w, rows * frame_h), (0, 0, 0, 0))
    for i, frame_img in enumerate(frames):
        x = (i % cols) * frame_w
        y = (i // cols) * frame_h
        sheet.paste(frame_img, (x, y))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_animator.py -v`
Expected: All 3 tests PASS

**Step 5: Commit**

```bash
git add tests/test_animator.py sprite_cli/animator.py
git commit -m "feat: add animator for GIF and sprite sheet generation"
```

---

### Task 6: Validator

**Files:**
- Create: `tests/test_validator.py`
- Create: `sprite_cli/validator.py`

**Step 1: Write the failing tests**

```python
import pytest
from sprite_cli.validator import validate_sprite_file
import tempfile, json
from pathlib import Path


def _write_json(tmp_dir, data):
    path = Path(tmp_dir) / "test.json"
    path.write_text(json.dumps(data))
    return path


def test_validate_valid_sprite():
    with tempfile.TemporaryDirectory() as tmp:
        path = _write_json(tmp, {
            "name": "test",
            "palette": {"r": "#FF0000"},
            "frames": {"idle": [[["r"]]]}
        })
        errors = validate_sprite_file(path)
        assert errors == []


def test_validate_missing_name():
    with tempfile.TemporaryDirectory() as tmp:
        path = _write_json(tmp, {
            "palette": {"r": "#FF0000"},
            "frames": {"idle": [[["r"]]]}
        })
        errors = validate_sprite_file(path)
        assert len(errors) > 0


def test_validate_bad_animation_ref():
    with tempfile.TemporaryDirectory() as tmp:
        path = _write_json(tmp, {
            "name": "test",
            "palette": {"r": "#FF0000"},
            "frames": {"idle": [[["r"]]]},
            "animations": {
                "bounce": {
                    "base": "nonexistent",
                    "transforms": []
                }
            }
        })
        errors = validate_sprite_file(path)
        assert any("nonexistent" in e for e in errors)


def test_validate_bad_json():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bad.json"
        path.write_text("not json at all")
        errors = validate_sprite_file(path)
        assert len(errors) > 0
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_validator.py -v`
Expected: FAIL — cannot import validate_sprite_file

**Step 3: Write the validator**

```python
import json
from pathlib import Path

from pydantic import ValidationError

from sprite_cli.models import SpriteDefinition


def validate_sprite_file(path: Path) -> list[str]:
    """Validate a sprite JSON file. Returns list of error strings (empty = valid)."""
    errors = []

    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        return [f"Failed to read JSON: {e}"]

    try:
        sprite = SpriteDefinition.model_validate(data)
    except ValidationError as e:
        return [str(err) for err in e.errors()]

    # Check animation base references
    for anim_name, anim in sprite.animations.items():
        if anim.base not in sprite.frames:
            errors.append(
                f"Animation '{anim_name}' references unknown frame set '{anim.base}'"
            )

    return errors
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_validator.py -v`
Expected: All 4 tests PASS

**Step 5: Commit**

```bash
git add tests/test_validator.py sprite_cli/validator.py
git commit -m "feat: add sprite JSON validator"
```

---

### Task 7: CLI Commands

**Files:**
- Create: `tests/test_cli.py`
- Modify: `sprite_cli/cli.py`

**Step 1: Write the failing tests**

```python
import json
import tempfile
from pathlib import Path

from click.testing import CliRunner

from sprite_cli.cli import cli


SAMPLE_SPRITE = {
    "name": "test",
    "palette": {"r": "#FF0000", "g": "#00FF00"},
    "frames": {
        "idle": [
            [["r", "g"], ["g", "r"]],
            [["g", "r"], ["r", "g"]],
        ]
    },
    "animations": {
        "bounce": {
            "base": "idle",
            "transforms": [
                [{"type": "translate", "y": -1}],
                [{"type": "translate", "y": 0}],
            ],
            "fps": 4,
        }
    }
}


def _write_sprite(tmp_dir):
    path = Path(tmp_dir) / "test.json"
    path.write_text(json.dumps(SAMPLE_SPRITE))
    return path


def test_render_command():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmp:
        sprite_path = _write_sprite(tmp)
        out = Path(tmp) / "out.png"
        result = runner.invoke(cli, ["render", str(sprite_path), "--output", str(out)])
        assert result.exit_code == 0
        assert out.exists()


def test_animate_command():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmp:
        sprite_path = _write_sprite(tmp)
        out = Path(tmp) / "out.gif"
        result = runner.invoke(cli, ["animate", str(sprite_path), "--output", str(out)])
        assert result.exit_code == 0
        assert out.exists()


def test_sheet_command():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmp:
        sprite_path = _write_sprite(tmp)
        out = Path(tmp) / "sheet.png"
        result = runner.invoke(cli, ["sheet", str(sprite_path), "--output", str(out)])
        assert result.exit_code == 0
        assert out.exists()


def test_validate_command():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmp:
        sprite_path = _write_sprite(tmp)
        result = runner.invoke(cli, ["validate", str(sprite_path)])
        assert result.exit_code == 0
        assert "valid" in result.output.lower()


def test_info_command():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmp:
        sprite_path = _write_sprite(tmp)
        result = runner.invoke(cli, ["info", str(sprite_path)])
        assert result.exit_code == 0
        assert "test" in result.output


def test_list_command():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmp:
        _write_sprite(tmp)
        result = runner.invoke(cli, ["list", tmp])
        assert result.exit_code == 0
        assert "test.json" in result.output
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py -v`
Expected: FAIL — commands not implemented

**Step 3: Write the full CLI**

```python
import json
from pathlib import Path

import click

from sprite_cli.animator import create_animation, create_sprite_sheet
from sprite_cli.models import SpriteDefinition
from sprite_cli.renderer import render_frame
from sprite_cli.validator import validate_sprite_file


def _load_sprite(path: str) -> SpriteDefinition:
    data = json.loads(Path(path).read_text())
    return SpriteDefinition.model_validate(data)


def _default_output(sprite_path: str, suffix: str) -> Path:
    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)
    name = Path(sprite_path).stem
    return out_dir / f"{name}{suffix}"


@click.group()
def cli():
    """Pixel-art sprite CLI."""
    pass


@cli.command()
@click.argument("file")
@click.option("--frame", default=None, help="Frame name to render (default: first)")
@click.option("--index", default=0, help="Frame index within the frame set")
@click.option("--output", "-o", default=None, help="Output PNG path")
def render(file, frame, index, output):
    """Render a sprite frame to PNG."""
    sprite = _load_sprite(file)
    frame_name = frame or next(iter(sprite.frames))
    out = Path(output) if output else _default_output(file, ".png")
    out.parent.mkdir(parents=True, exist_ok=True)
    img = render_frame(sprite, frame_name, frame_index=index)
    img.save(out)
    click.echo(f"Rendered {sprite.name} -> {out}")


@cli.command()
@click.argument("file")
@click.option("--animation", "-a", default=None, help="Animation name")
@click.option("--frame", default=None, help="Frame set name (for frame-by-frame)")
@click.option("--fps", default=None, type=int, help="Frames per second")
@click.option("--output", "-o", default=None, help="Output GIF path")
def animate(file, animation, frame, fps, output):
    """Generate an animated GIF."""
    sprite = _load_sprite(file)
    out = Path(output) if output else _default_output(file, ".gif")

    # Default: use first animation if available, else first frame set
    anim_name = animation
    frame_name = frame
    if not anim_name and not frame_name:
        if sprite.animations:
            anim_name = next(iter(sprite.animations))
        else:
            frame_name = next(iter(sprite.frames))

    create_animation(sprite, output_path=out, animation_name=anim_name, frame_name=frame_name, fps=fps)
    click.echo(f"Animated {sprite.name} -> {out}")


@cli.command()
@click.argument("file")
@click.option("--frame", default=None, help="Frame set name")
@click.option("--columns", "-c", default=None, type=int, help="Columns in sheet")
@click.option("--output", "-o", default=None, help="Output PNG path")
def sheet(file, frame, columns, output):
    """Generate a sprite sheet."""
    sprite = _load_sprite(file)
    frame_name = frame or next(iter(sprite.frames))
    out = Path(output) if output else _default_output(file, "-sheet.png")
    create_sprite_sheet(sprite, frame_name=frame_name, output_path=out, columns=columns)
    click.echo(f"Sprite sheet {sprite.name} -> {out}")


@cli.command()
@click.argument("file")
def validate(file):
    """Validate a sprite JSON file."""
    errors = validate_sprite_file(Path(file))
    if errors:
        for e in errors:
            click.echo(f"  Error: {e}", err=True)
        raise SystemExit(1)
    else:
        click.echo(f"Valid: {file}")


@cli.command()
@click.argument("file")
def info(file):
    """Show sprite metadata."""
    sprite = _load_sprite(file)
    click.echo(f"Name: {sprite.name}")
    click.echo(f"Size: {sprite.size or 'auto'}")
    click.echo(f"Palette: {len(sprite.palette)} colors")
    click.echo(f"Frame sets: {', '.join(sprite.frames.keys())}")
    for name, frames in sprite.frames.items():
        click.echo(f"  {name}: {len(frames)} frame(s)")
    if sprite.animations:
        click.echo(f"Animations: {', '.join(sprite.animations.keys())}")


@cli.command("list")
@click.argument("directory", default=".")
def list_sprites(directory):
    """List sprite JSON files in a directory."""
    for path in sorted(Path(directory).glob("*.json")):
        try:
            data = json.loads(path.read_text())
            name = data.get("name", "?")
            click.echo(f"  {path.name} ({name})")
        except (json.JSONDecodeError, OSError):
            click.echo(f"  {path.name} (invalid)")


if __name__ == "__main__":
    cli()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py -v`
Expected: All 6 tests PASS

**Step 5: Commit**

```bash
git add tests/test_cli.py sprite_cli/cli.py
git commit -m "feat: add all CLI commands (render, animate, sheet, validate, info, list)"
```

---

### Task 8: Example Robot Sprite + End-to-End Test

**Files:**
- Create: `examples/robot.json`
- Create: `tests/test_e2e.py`

**Step 1: Create the example robot sprite**

```json
{
  "name": "robot",
  "size": 32,
  "palette": {
    "b": "#4A90D9",
    "d": "#2C5F8A",
    "e": "#FFFFFF",
    "p": "#333333",
    "m": "#FF6B6B",
    "a": "#7BB3E0"
  },
  "frames": {
    "idle": [
      [
        [null,null,null,"d","d","d","d",null,null,null],
        [null,null,"d","b","b","b","b","d",null,null],
        [null,"d","b","b","b","b","b","b","d",null],
        [null,"d","b","e","e","b","e","e","d",null],
        [null,"d","b","e","p","b","e","p","d",null],
        [null,"d","b","b","b","b","b","b","d",null],
        [null,null,"d","b","m","m","b","d",null,null],
        [null,null,null,"d","d","d","d",null,null,null],
        [null,null,"a","b","b","b","b","a",null,null],
        [null,null,null,"b","b","b","b",null,null,null],
        [null,null,null,"d","d","d","d",null,null,null],
        [null,null,"d",null,null,null,null,"d",null,null]
      ]
    ]
  },
  "animations": {
    "bounce": {
      "base": "idle",
      "transforms": [
        [{"type": "translate", "y": 0}],
        [{"type": "translate", "y": -1}],
        [{"type": "translate", "y": -2}],
        [{"type": "translate", "y": -1}],
        [{"type": "translate", "y": 0}]
      ],
      "fps": 6,
      "loop": true
    }
  }
}
```

**Step 2: Write e2e test**

```python
import tempfile
from pathlib import Path

from click.testing import CliRunner
from PIL import Image

from sprite_cli.cli import cli


def test_e2e_robot():
    runner = CliRunner()
    robot = str(Path(__file__).parent.parent / "examples" / "robot.json")

    with tempfile.TemporaryDirectory() as tmp:
        # Render
        png = Path(tmp) / "robot.png"
        result = runner.invoke(cli, ["render", robot, "-o", str(png)])
        assert result.exit_code == 0
        img = Image.open(png)
        assert img.size == (32, 32)

        # Animate
        gif = Path(tmp) / "robot.gif"
        result = runner.invoke(cli, ["animate", robot, "-o", str(gif)])
        assert result.exit_code == 0
        anim = Image.open(gif)
        assert anim.n_frames == 5

        # Validate
        result = runner.invoke(cli, ["validate", robot])
        assert result.exit_code == 0

        # Info
        result = runner.invoke(cli, ["info", robot])
        assert result.exit_code == 0
        assert "robot" in result.output
```

**Step 3: Run all tests**

Run: `pytest -v`
Expected: All tests PASS

**Step 4: Commit**

```bash
git add examples/robot.json tests/test_e2e.py
git commit -m "feat: add example robot sprite and end-to-end test"
```

---

## Summary

| Task | What | Tests |
|------|------|-------|
| 1 | Project scaffolding | Manual verify |
| 2 | Pydantic models | 4 tests |
| 3 | Renderer (PNG) | 4 tests |
| 4 | Transforms | 7 tests |
| 5 | Animator (GIF + sheets) | 3 tests |
| 6 | Validator | 4 tests |
| 7 | CLI commands | 6 tests |
| 8 | Example + E2E | 1 test |

**Total: 8 tasks, 29 tests, ~8 commits**
