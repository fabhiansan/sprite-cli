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
