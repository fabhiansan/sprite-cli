import json
from pathlib import Path

from pydantic import ValidationError

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

    return errors
