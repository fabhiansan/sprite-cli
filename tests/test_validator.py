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
            "frames": {"idle": [[["r"]]]},
            "anchors": {"face_center": {"x": 0, "y": 0}},
            "regions": {"face": {"x": 0, "y": 0, "w": 1, "h": 1}},
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


def test_validate_anchor_out_of_bounds():
    with tempfile.TemporaryDirectory() as tmp:
        path = _write_json(tmp, {
            "name": "test",
            "palette": {"r": "#FF0000"},
            "frames": {"idle": [[["r"]]]},
            "anchors": {"face_center": {"x": 2, "y": 0}},
        })
        errors = validate_sprite_file(path)
        assert any("out of bounds" in e for e in errors)


def test_validate_region_out_of_bounds():
    with tempfile.TemporaryDirectory() as tmp:
        path = _write_json(tmp, {
            "name": "test",
            "palette": {"r": "#FF0000"},
            "frames": {"idle": [[["r"]]]},
            "regions": {"face": {"x": 0, "y": 0, "w": 2, "h": 1}},
        })
        errors = validate_sprite_file(path)
        assert any("exceeds canvas bounds" in e for e in errors)
