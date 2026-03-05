import tempfile
from pathlib import Path

from click.testing import CliRunner
from PIL import Image

from sprite_cli.cli import cli


def test_e2e_robot():
    runner = CliRunner()
    robot = str(Path(__file__).parent.parent / "examples" / "robot.json")

    with tempfile.TemporaryDirectory() as tmp:
        # Render
        png = Path(tmp) / "robot.png"
        result = runner.invoke(cli, ["render", robot, "-o", str(png)])
        assert result.exit_code == 0, result.output
        img = Image.open(png)
        assert img.size == (32, 32)

        # Animate
        gif = Path(tmp) / "robot.gif"
        result = runner.invoke(cli, ["animate", robot, "-o", str(gif)])
        assert result.exit_code == 0, result.output
        anim = Image.open(gif)
        assert anim.n_frames == 5

        # Validate
        result = runner.invoke(cli, ["validate", robot])
        assert result.exit_code == 0

        # Info
        result = runner.invoke(cli, ["info", robot])
        assert result.exit_code == 0
        assert "robot" in result.output
