import json
from pathlib import Path

import click

from sprite_cli.animator import create_animation, create_sprite_sheet
from sprite_cli.models import SpriteDefinition
from sprite_cli.renderer import render_frame
from sprite_cli.validator import validate_sprite_file


def _load_sprite(path: str) -> SpriteDefinition:
    data = json.loads(Path(path).read_text())
    return SpriteDefinition.model_validate(data)


def _default_output(sprite_path: str, suffix: str) -> Path:
    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)
    name = Path(sprite_path).stem
    return out_dir / f"{name}{suffix}"


@click.group()
def cli():
    """Pixel-art sprite CLI."""
    pass


@cli.command()
@click.argument("file")
@click.option("--frame", default=None, help="Frame name to render (default: first)")
@click.option("--index", default=0, help="Frame index within the frame set")
@click.option("--output", "-o", default=None, help="Output PNG path")
def render(file, frame, index, output):
    """Render a sprite frame to PNG."""
    sprite = _load_sprite(file)
    frame_name = frame or next(iter(sprite.frames))
    out = Path(output) if output else _default_output(file, ".png")
    out.parent.mkdir(parents=True, exist_ok=True)
    img = render_frame(sprite, frame_name, frame_index=index)
    img.save(out)
    click.echo(f"Rendered {sprite.name} -> {out}")


@cli.command()
@click.argument("file")
@click.option("--animation", "-a", default=None, help="Animation name")
@click.option("--frame", default=None, help="Frame set name (for frame-by-frame)")
@click.option("--fps", default=None, type=int, help="Frames per second")
@click.option("--output", "-o", default=None, help="Output GIF path")
def animate(file, animation, frame, fps, output):
    """Generate an animated GIF."""
    sprite = _load_sprite(file)
    out = Path(output) if output else _default_output(file, ".gif")

    anim_name = animation
    frame_name = frame
    if not anim_name and not frame_name:
        if sprite.animations:
            anim_name = next(iter(sprite.animations))
        else:
            frame_name = next(iter(sprite.frames))

    create_animation(sprite, output_path=out, animation_name=anim_name, frame_name=frame_name, fps=fps)
    click.echo(f"Animated {sprite.name} -> {out}")


@cli.command()
@click.argument("file")
@click.option("--frame", default=None, help="Frame set name")
@click.option("--columns", "-c", default=None, type=int, help="Columns in sheet")
@click.option("--output", "-o", default=None, help="Output PNG path")
def sheet(file, frame, columns, output):
    """Generate a sprite sheet."""
    sprite = _load_sprite(file)
    frame_name = frame or next(iter(sprite.frames))
    out = Path(output) if output else _default_output(file, "-sheet.png")
    create_sprite_sheet(sprite, frame_name=frame_name, output_path=out, columns=columns)
    click.echo(f"Sprite sheet {sprite.name} -> {out}")


@cli.command()
@click.argument("file")
def validate(file):
    """Validate a sprite JSON file."""
    errors = validate_sprite_file(Path(file))
    if errors:
        for e in errors:
            click.echo(f"  Error: {e}", err=True)
        raise SystemExit(1)
    else:
        click.echo(f"Valid: {file}")


@cli.command()
@click.argument("file")
def info(file):
    """Show sprite metadata."""
    sprite = _load_sprite(file)
    click.echo(f"Name: {sprite.name}")
    click.echo(f"Size: {sprite.size or 'auto'}")
    click.echo(f"Palette: {len(sprite.palette)} colors")
    click.echo(f"Frame sets: {', '.join(sprite.frames.keys())}")
    for name, frames in sprite.frames.items():
        click.echo(f"  {name}: {len(frames)} frame(s)")
    if sprite.animations:
        click.echo(f"Animations: {', '.join(sprite.animations.keys())}")


@cli.command("list")
@click.argument("directory", default=".")
def list_sprites(directory):
    """List sprite JSON files in a directory."""
    for path in sorted(Path(directory).glob("*.json")):
        try:
            data = json.loads(path.read_text())
            name = data.get("name", "?")
            click.echo(f"  {path.name} ({name})")
        except (json.JSONDecodeError, OSError):
            click.echo(f"  {path.name} (invalid)")


@cli.command("import")
@click.argument("image")
@click.option("--name", "-n", default=None, help="Sprite name (default: filename)")
@click.option("--output", "-o", default=None, help="Output JSON path")
def import_sprite(image, name, output):
    """Import a PNG image as a sprite definition."""
    from sprite_cli.importer import import_image as do_import
    image_path = Path(image)
    sprite_data = do_import(image_path, name=name)
    out = Path(output) if output else _default_output(image, ".json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(sprite_data, indent=2))
    click.echo(f"Imported {image_path.name} -> {out}")


if __name__ == "__main__":
    cli()
