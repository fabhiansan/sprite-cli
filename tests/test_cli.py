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
    },
    "anchors": {
        "face_center": {"x": 1, "y": 0},
        "left_hand": {"x": 0, "y": 1}
    },
    "regions": {
        "face": {"x": 0, "y": 0, "w": 2, "h": 1}
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
        assert "face_center" in result.output


def test_analyze_command():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmp:
        sprite_path = _write_sprite(tmp)
        result = runner.invoke(cli, ["analyze", str(sprite_path)])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["name"] == "test"
        assert data["canvas"] == {"width": 2, "height": 2}
        assert data["anchors"]["face_center"]["x"] == 1
        assert data["regions"]["face"]["w"] == 2


def test_list_command():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmp:
        _write_sprite(tmp)
        result = runner.invoke(cli, ["list", tmp])
        assert result.exit_code == 0
        assert "test.json" in result.output


def test_import_command():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmp:
        # Create a simple test PNG
        from PIL import Image
        img = Image.new("RGBA", (4, 4), (0, 0, 0, 0))
        img.putpixel((0, 0), (255, 0, 0, 255))
        img.putpixel((1, 1), (0, 255, 0, 255))
        png_path = Path(tmp) / "test.png"
        img.save(png_path)

        out = Path(tmp) / "imported.json"
        result = runner.invoke(cli, ["import", str(png_path), "--output", str(out)])
        assert result.exit_code == 0, result.output
        assert out.exists()

        # Verify the output is valid JSON and a valid sprite
        import json
        data = json.loads(out.read_text())
        assert data["name"] == "test"
        assert "palette" in data
        assert "frames" in data
