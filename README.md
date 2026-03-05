# sprite-cli

A pixel-art sprite CLI designed for AI-driven game asset creation. Write JSON sprite definitions, render them to PNG, animated GIF, and sprite sheets.

Built for creating assets for a kids' educational mobile game (numbers, hijaiyah letters, etc.).

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
