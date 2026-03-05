# Sprite CLI Design

## Purpose
A Python CLI tool that renders pixel-art sprites from JSON definitions. Designed for AI (Claude) to generate sprite assets for a kids' educational mobile game (numbers, hijaiyah letters, etc.).

## Flow
1. AI writes JSON sprite definitions (pixel grids + animation data)
2. CLI renders JSON to PNG, animated GIF, or sprite sheets
3. Assets used in a web-based mobile game

## JSON Format

```json
{
  "name": "robot",
  "size": 32,
  "palette": {
    "body": "#4A90D9",
    "eye": "#FFFFFF",
    "bg": null
  },
  "frames": {
    "idle": [
      [["null", "null", "body", "body", "null"],
       ["null", "body", "eye", "body", "null"],
       ["body", "body", "body", "body", "body"]]
    ]
  },
  "animations": {
    "bounce": {
      "base": "idle",
      "transforms": [
        {"type": "translate", "y": -2},
        {"type": "translate", "y": 0}
      ],
      "fps": 4
    }
  }
}
```

- `frames` — frame-by-frame (2D arrays of palette keys or hex colors, null for transparent)
- `animations` — transformation-based, referencing a base frame
- `size` — auto-determined but overridable

## CLI Commands

```
sprite render <file.json>              # Render to PNG
sprite animate <file.json>             # Generate animated GIF
sprite sheet <file.json>               # Generate sprite sheet
sprite validate <file.json>            # Validate JSON
sprite list <directory>                # List sprite definitions
sprite info <file.json>                # Show sprite metadata
```

Output defaults to `./output/`, transparent background, auto-named files.

## Transforms

| Transform | Parameters | Use |
|-----------|-----------|-----|
| translate | x, y | Shift sprite |
| rotate | angle (90/180/270) | Rotate sprite |
| flip | axis (h/v) | Mirror sprite |
| scale | factor | Resize sprite |
| recolor | from, to | Swap palette color |

Transforms can be chained per frame. For complex animations (waving arm), use frame-by-frame instead.

## Project Structure

```
sprite_cli/
  sprite_cli/
    __init__.py
    cli.py          # Click CLI entry point
    models.py       # Pydantic data models
    renderer.py     # Pillow PNG rendering
    animator.py     # GIF + sprite sheet generation
    transforms.py   # Transformation logic
    validator.py    # JSON validation
  examples/
    robot.json
  output/
  pyproject.toml
  README.md
```

## Dependencies
- click — CLI framework
- pillow — image rendering
- pydantic — JSON validation & data models

## Tech Decisions
- Python with pip install -e . for local dev
- Web-based game (PWA/React Native) consuming the sprite assets
- Pixel art style, adaptive sizing
