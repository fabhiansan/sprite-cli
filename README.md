# sprite-cli

A pixel-art sprite CLI designed for AI-driven game asset creation. Write JSON sprite definitions, render them to PNG, animated GIF, and sprite sheets.

Built for creating assets for a kids' educational mobile game (numbers, hijaiyah letters, etc.).

<p align="center">
  <img src="assets/robot.png" width="128" alt="Robot sprite">
  <img src="assets/robot-bounce.gif" width="128" alt="Robot bounce animation">
  <img src="assets/robot-walk.gif" width="128" alt="Robot walk animation">
  <img src="assets/frog.png" width="128" alt="Frog sprite">
  <img src="assets/frog-bounce.gif" width="128" alt="Frog bounce animation">
  <img src="assets/star.png" width="128" alt="Star sprite">
  <img src="assets/star-sparkle.gif" width="128" alt="Star sparkle animation">
</p>

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick Start

```bash
# Render the example robot sprite
sprite render examples/robot.json -o output/robot.png

# Create a bounce animation
sprite animate examples/robot.json -a bounce -o output/robot.gif

# Generate a sprite sheet
sprite sheet examples/robot.json -o output/robot-sheet.png
```

## Commands

| Command | Description |
|---------|-------------|
| `sprite render <file>` | Render a sprite frame to PNG |
| `sprite animate <file>` | Generate an animated GIF |
| `sprite sheet <file>` | Generate a sprite sheet |
| `sprite validate <file>` | Validate a sprite JSON file |
| `sprite info <file>` | Show sprite metadata |
| `sprite list [dir]` | List sprite JSON files |
| `sprite import <image>` | Import a PNG as sprite JSON |

## JSON Format

```json
{
  "name": "robot",
  "size": 32,
  "palette": {
    "b": "#4A90D9",
    "d": "#2C5F8A",
    "e": "#FFFFFF",
    "p": "#333333"
  },
  "frames": {
    "idle": [
      [
        [null, null, "d", "d", null, null],
        [null, "d", "e", "e", "d", null],
        ["d", "b", "e", "e", "b", "d"],
        ["d", "b", "b", "b", "b", "d"],
        [null, "d", "b", "b", "d", null],
        [null, "d", null, null, "d", null]
      ]
    ]
  },
  "animations": {
    "bounce": {
      "base": "idle",
      "transforms": [
        [{"type": "translate", "y": 0}],
        [{"type": "translate", "y": -2}],
        [{"type": "translate", "y": 0}]
      ],
      "fps": 6
    }
  }
}
```

- **palette** — short color keys mapped to hex values. `null` = transparent.
- **frames** — named frame sets. Each frame is a 2D grid of palette keys or `null`.
- **animations** — transform-based animations referencing a base frame.
- **size** — output image size (grid scales up via nearest-neighbor).

## Animation

### Transform-based

For simple motions (bounce, slide, flash). Applies transforms to a base frame:

```bash
sprite animate sprite.json -a bounce -o bounce.gif
```

Available transforms: `translate`, `rotate`, `flip`, `scale`, `recolor`.

### Frame-by-frame

For complex motions (walk, wave). Define multiple frames in a frame set:

```bash
sprite animate sprite.json --frame walk -o walk.gif
```

## Importing Existing Art

Convert any PNG to a sprite JSON definition:

```bash
sprite import character.png -o character.json
```

Extracts unique colors into an auto-generated palette and builds the pixel grid. Edit the JSON to rename palette keys, add animations, then re-render.

## AI Workflow

This CLI is designed to be used by AI assistants like Claude. The workflow:

1. AI writes a sprite JSON definition (pixel grid + palette + animations)
2. CLI renders it to PNG/GIF
3. AI previews the output and iterates

A **sprite-creator skill** is included in `sprite-creator-skill/` for Claude Code integration.

## Tests

```bash
pytest -v
```

34 tests covering models, renderer, transforms, animator, validator, CLI, importer, and end-to-end.

```
tests/test_animator.py::test_create_animation_from_frames PASSED
tests/test_animator.py::test_create_animation_from_transforms PASSED
tests/test_animator.py::test_create_sprite_sheet PASSED
tests/test_cli.py::test_render_command PASSED
tests/test_cli.py::test_animate_command PASSED
tests/test_cli.py::test_sheet_command PASSED
tests/test_cli.py::test_validate_command PASSED
tests/test_cli.py::test_info_command PASSED
tests/test_cli.py::test_list_command PASSED
tests/test_cli.py::test_import_command PASSED
tests/test_e2e.py::test_e2e_robot PASSED
tests/test_models.py::test_parse_minimal_sprite PASSED
tests/test_models.py::test_parse_sprite_with_animation PASSED
tests/test_models.py::test_parse_sprite_with_hex_colors_in_grid PASSED
tests/test_models.py::test_invalid_sprite_missing_name PASSED
tests/test_renderer.py::test_render_simple_frame PASSED
tests/test_renderer.py::test_render_transparent_pixels PASSED
tests/test_renderer.py::test_render_with_size_scaling PASSED
tests/test_renderer.py::test_render_hex_color_in_grid PASSED
tests/test_transforms.py::test_translate PASSED
tests/test_transforms.py::test_translate_up PASSED
tests/test_transforms.py::test_flip_horizontal PASSED
tests/test_transforms.py::test_flip_vertical PASSED
tests/test_transforms.py::test_rotate_90 PASSED
tests/test_transforms.py::test_recolor PASSED
tests/test_transforms.py::test_scale PASSED
tests/test_validator.py::test_validate_valid_sprite PASSED
tests/test_validator.py::test_validate_missing_name PASSED
tests/test_validator.py::test_validate_bad_animation_ref PASSED
tests/test_validator.py::test_validate_bad_json PASSED
tests/test_importer.py::test_import_simple_image PASSED
tests/test_importer.py::test_import_fully_transparent PASSED
tests/test_importer.py::test_import_preserves_colors PASSED
tests/test_importer.py::test_import_roundtrip PASSED

34 passed in 0.07s
```
