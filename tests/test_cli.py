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
        assert result.exit_code == 0, result.output
        assert out.exists()


def test_animate_command():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmp:
        sprite_path = _write_sprite(tmp)
        out = Path(tmp) / "out.gif"
        result = runner.invoke(cli, ["animate", str(sprite_path), "--output", str(out)])
        assert result.exit_code == 0, result.output
        assert out.exists()


def test_sheet_command():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmp:
        sprite_path = _write_sprite(tmp)
        out = Path(tmp) / "sheet.png"
        result = runner.invoke(cli, ["sheet", str(sprite_path), "--output", str(out)])
        assert result.exit_code == 0, result.output
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
