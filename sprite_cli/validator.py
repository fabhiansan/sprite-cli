import json
from pathlib import Path

from pydantic import ValidationError

from sprite_cli.analysis import sprite_canvas_size
from sprite_cli.models import SpriteDefinition


def validate_sprite_file(path: Path) -> list[str]:
    errors = []

    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        return [f"Failed to read JSON: {e}"]

    try:
        sprite = SpriteDefinition.model_validate(data)
    except ValidationError as e:
        return [str(err) for err in e.errors()]

    for anim_name, anim in sprite.animations.items():
        if anim.base not in sprite.frames:
            errors.append(
                f"Animation '{anim_name}' references unknown frame set '{anim.base}'"
            )

    canvas_width, canvas_height = sprite_canvas_size(sprite)

    for anchor_name, anchor in sprite.anchors.items():
        if not (0 <= anchor.x < canvas_width) or not (0 <= anchor.y < canvas_height):
            errors.append(
                f"Anchor '{anchor_name}' is out of bounds for canvas {canvas_width}x{canvas_height}"
            )

    for region_name, region in sprite.regions.items():
        if region.x < 0 or region.y < 0:
            errors.append(f"Region '{region_name}' must not start at negative coordinates")
            continue
        if region.x + region.w > canvas_width or region.y + region.h > canvas_height:
            errors.append(
                f"Region '{region_name}' exceeds canvas bounds {canvas_width}x{canvas_height}"
            )

    return errors
