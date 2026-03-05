---
name: sprite-creator
description: Create pixel-art sprites, characters, and animations using the sprite-cli tool. Use this skill whenever the user asks to create a sprite, pixel art, game character, animated character, sprite sheet, or any visual game asset. Also use it when the user wants to modify existing sprites, add animation frames, or import/export pixel art. Triggers on mentions of sprites, pixel art, game assets, characters for games, bouncing/walking/idle animations, or anything related to creating visual assets for 2D games.
---

# Sprite Creator

Create pixel-art sprites by writing JSON definitions and rendering them with the `sprite` CLI.

## Prerequisites

The sprite-cli must be installed. The project lives at the root of this repository. If the virtualenv exists at `.venv`, activate it with `source .venv/bin/activate` before running any `sprite` commands.

## Workflow

1. **Design** — decide what to draw (character, object, letter, number)
2. **Choose palette** — pick 3-6 colors that work together
3. **Draw the pixel grid** — write the 2D array row by row
4. **Validate** — run `sprite validate <file>.json`
5. **Render** — run `sprite render <file>.json -o output/<name>.png`
6. **Preview** — use the Read tool to view the rendered PNG
7. **Iterate** — adjust pixels, re-render, repeat until it looks right
8. **Animate** — add animation frames or transforms, then `sprite animate <file>.json -o output/<name>.gif`

Always validate and render after creating or modifying a sprite. Always preview the output with the Read tool so you can see what you made and fix issues.

## JSON Schema (exact fields)

```json
{
  "name": "character_name",
  "size": 32,
  "palette": {
    "b": "#4A90D9",
    "d": "#2C5F8A",
    "e": "#FFFFFF"
  },
  "frames": {
    "idle": [
      [
        [null, "b", "b", null],
        ["b", "e", "e", "b"],
        ["b", "b", "b", "b"],
        [null, "b", "b", null]
      ]
    ]
  },
  "animations": {
    "bounce": {
      "base": "idle",
      "transforms": [
        [{"type": "translate", "y": 0}],
        [{"type": "translate", "y": -1}],
        [{"type": "translate", "y": 0}]
      ],
      "fps": 6,
      "loop": true
    }
  }
}
```

### Required and optional fields

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `name` | Yes | string | Sprite identifier |
| `size` | No | int | Output image size in px. Grid scales up via nearest-neighbor. Use 32 for game sprites. Omit for 1:1. |
| `palette` | Yes | object | Map of short keys (1-2 chars) to hex color strings. `null` value = transparent. |
| `frames` | Yes | object | Map of frame set names to arrays of frames. Each frame is a 2D array of rows. Each pixel is a palette key, hex string, or `null`. |
| `animations` | No | object | Map of animation names to animation objects (see below). |

### Animation object fields

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `base` | **Yes** | string | Name of a frame set in `frames`. This is the base frame the transforms are applied to. |
| `transforms` | Yes | array | List of transform steps. Each step is an array of transform objects. |
| `fps` | No | int | Frames per second (default: 4) |
| `loop` | No | bool | Whether to loop (default: true) |

The `base` field is required and must reference an existing frame set name. Do NOT use `frame_set` or any other name — the field is called `base`.

## Two Animation Approaches

Choose ONE approach per animation. Do not mix them.

### Approach 1: Transform-based (simple motions)

For: bouncing, sliding, flipping, color flashing. Put a base frame in `frames`, then define transforms in `animations`.

```json
{
  "frames": {
    "idle": [ [[...single frame...]] ]
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

Render with: `sprite animate <file>.json -a bounce -o output/bounce.gif`

**Available transforms:**

| Type | Parameters | What it does |
|------|-----------|-------------|
| `translate` | `x`, `y` | Shift the sprite by pixels |
| `rotate` | `angle` (90, 180, 270) | Rotate the whole sprite |
| `flip` | `axis` ("horizontal" or "vertical") | Mirror the sprite |
| `scale` | `factor` (e.g. 0.5, 2.0) | Scale the sprite |
| `recolor` | `from_color`, `to_color` | Swap a palette key for another |

### Approach 2: Frame-by-frame (complex motions)

For: walking, waving, expressions — anything that changes the shape of the sprite. Put multiple frames in a frame set. Do NOT add an `animations` entry for this — just use `--frame` when animating.

```json
{
  "frames": {
    "idle": [ [[...single frame...]] ],
    "walk": [
      [[...frame 1...]],
      [[...frame 2...]],
      [[...frame 3...]]
    ]
  }
}
```

Render with: `sprite animate <file>.json --frame walk -o output/walk.gif`

**When using frame-by-frame, always pass `--frame <name>` to the animate command.** If you omit it, the CLI will look for a transform-based animation in `animations` first, and fail if there isn't one or if it's empty.

### How to draw a walk cycle

Walking means the legs actually move between frames. Do NOT use translate transforms for walking — that just slides the whole sprite without moving any body parts. Instead, draw 4 frames where the leg pixels change position:

1. **Stand** — both legs centered under the body
2. **Step left** — left leg extends 1-2px left, right leg stays or tucks in
3. **Stand** — back to neutral
4. **Step right** — right leg extends 1-2px right, left leg stays or tucks in

The key principle: the body and head stay mostly the same across frames, but the bottom rows (legs/feet) change pixel positions. Copy your idle frame 4 times, then only edit the leg rows in each copy.

Example for a simple character (showing just the bottom 3 rows):

```
Frame 1 (stand):    Frame 2 (step L):   Frame 3 (stand):    Frame 4 (step R):
  [null,"b","b",null] ["b","b",null,null]  [null,"b","b",null]  [null,null,"b","b"]
  [null,"d","d",null] ["d",null,null,"d"]  [null,"d","d",null]  ["d",null,null,"d"]
  [null,"d","d",null] ["d",null,null,"d"]  [null,"d","d",null]  ["d",null,null,"d"]
```

The same principle applies to waving — copy the idle frame, then change the arm/hand pixels in each frame to show the hand moving up and down.

**The rule: if the animation involves body parts changing position, use frame-by-frame. Copy the base frame, then edit only the pixels that move.**

### Which approach to use

- Walking, waving, blinking, facial changes → **frame-by-frame** (the sprite shape changes)
- Bouncing, sliding, spinning, color flashing → **transform-based** (the sprite shape stays the same)
- Both in one sprite → put the simple motion in `animations` and the complex motion as multiple frames in `frames`. Use separate CLI calls to render each.

## Drawing Pixel Art

Think in rows from top to bottom, each row left to right. Use `null` for transparent/empty pixels.

**Tips for good pixel art:**
- Start with the silhouette — fill in the outline first, then add detail
- Use 2-3 shades per color for depth (light, base, dark)
- Keep characters symmetrical when possible — it reads better at small sizes
- Eyes and mouth are the most important details for characters — make them pop
- Leave 1-2 pixels of padding around the sprite edge for breathing room

**Recommended grid sizes:**
- Simple icons/items: 8x8 or 10x10
- Characters: 10x12 to 16x16
- Detailed characters: 16x20 to 20x24

## Palette Design

- **Body colors**: pick a base, then a darker shade for outlines/shadows and a lighter shade for highlights
- **Feature colors**: 1-2 accent colors for eyes, mouth, accessories
- **Keep it small**: 4-6 colors is ideal. More than 8 gets hard to manage.

**Example palettes:**

Robot: `{"b": "#4A90D9", "d": "#2C5F8A", "e": "#FFFFFF", "p": "#333333", "m": "#FF6B6B"}`

Cat: `{"o": "#F5A623", "d": "#C17D10", "e": "#4A4A4A", "w": "#FFFFFF", "n": "#FF9999"}`

Frog: `{"g": "#4CAF50", "d": "#2E7D32", "e": "#FFFFFF", "p": "#333333", "m": "#FF5252"}`

## CLI Commands

```bash
# Render a single frame to PNG
sprite render <file>.json -o output/<name>.png

# Render a specific frame from a frame set
sprite render <file>.json --frame walk --index 1 -o output/<name>-walk1.png

# Animate using a transform-based animation
sprite animate <file>.json -a bounce -o output/<name>-bounce.gif

# Animate using frame-by-frame (MUST pass --frame)
sprite animate <file>.json --frame walk -o output/<name>-walk.gif

# Create sprite sheet
sprite sheet <file>.json -o output/<name>-sheet.png

# Validate JSON
sprite validate <file>.json

# Show sprite info
sprite info <file>.json

# List sprites in a directory
sprite list examples/

# Import existing PNG to JSON (for editing existing art)
sprite import <image>.png -o <name>.json
sprite import <image>.png --name "my_sprite" -o sprites/<name>.json
```

## Importing Existing Art

To continue working on existing pixel art:

```bash
sprite import existing.png -o sprite.json
```

This extracts all unique colors into an auto-generated palette (c0, c1, c2...) and builds the pixel grid. You can then rename palette keys to be more descriptive, add animations, and re-render.

## Common Mistakes to Avoid

1. **Using `frame_set` instead of `base`** in animation objects. The field is called `base` and it must reference a frame set name from `frames`.
2. **Mixing animation approaches** — if you have frame-by-frame frames in `walk`, don't also create an `animations.walk` entry with transforms. Pick one.
3. **Forgetting `--frame` flag** — for frame-by-frame animations, always use `sprite animate --frame <name>`. Without it, the CLI looks for transform-based animations.
4. **Not validating** — always run `sprite validate` before rendering. It catches schema issues early.
5. **Not previewing** — always use the Read tool to look at the rendered PNG/GIF. Pixel art often needs iteration.

## Example: Full Character Creation

1. Write the JSON with palette and idle frame
2. Save to `examples/cat.json`
3. Run `sprite validate examples/cat.json`
4. Run `sprite render examples/cat.json -o output/cat.png`
5. View the output with the Read tool
6. Adjust pixels if needed, re-render
7. Add a bounce animation (transform-based) or walk frames (frame-by-frame)
8. Run `sprite animate examples/cat.json -a bounce -o output/cat-bounce.gif`
9. View the GIF

Always save sprites to the `examples/` directory and render output to `output/`.
