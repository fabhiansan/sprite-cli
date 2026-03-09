from pathlib import Path

from PIL import Image

from sprite_cli.models import SpriteDefinition
from sprite_cli.renderer import render_frame, render_pixels
from sprite_cli.transforms import apply_transform


def _generate_transform_frames(
    sprite: SpriteDefinition,
    animation_name: str,
) -> list[Image.Image]:
    anim = sprite.animations[animation_name]
    base_frame = sprite.frames[anim.base][0]
    images = []

    for transform_step in anim.transforms:
        if isinstance(transform_step, list):
            transforms = transform_step
        else:
            transforms = [transform_step]

        frame = [list(row) for row in base_frame]
        for t in transforms:
            frame = apply_transform(frame, t)

        img = render_pixels(frame, sprite.palette, size=sprite.size)
        images.append(img)

    return images


def create_animation(
    sprite: SpriteDefinition,
    output_path: Path,
    frame_name: str | None = None,
    animation_name: str | None = None,
    fps: int | None = None,
) -> None:
    if animation_name and animation_name in sprite.animations:
        images = _generate_transform_frames(sprite, animation_name)
        fps = fps or sprite.animations[animation_name].fps
    elif frame_name and frame_name in sprite.frames:
        images = [
            render_frame(sprite, frame_name, i)
            for i in range(len(sprite.frames[frame_name]))
        ]
        fps = fps or 4
    else:
        raise ValueError("Must specify either frame_name or animation_name")

    if not images:
        raise ValueError("No frames to animate")

    fps = fps or 4
    duration = int(1000 / fps)
    loop = 0
    if animation_name and animation_name in sprite.animations and not sprite.animations[animation_name].loop:
        loop = 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=loop,
        disposal=2,
    )


def create_sprite_sheet(
    sprite: SpriteDefinition,
    frame_name: str,
    output_path: Path,
    columns: int | None = None,
) -> None:
    frames = [
        render_frame(sprite, frame_name, i)
        for i in range(len(sprite.frames[frame_name]))
    ]

    if not frames:
        raise ValueError("No frames to create sheet from")

    frame_w, frame_h = frames[0].size
    n = len(frames)
    cols = columns or n
    rows = (n + cols - 1) // cols

    sheet = Image.new("RGBA", (cols * frame_w, rows * frame_h), (0, 0, 0, 0))
    for i, frame_img in enumerate(frames):
        x = (i % cols) * frame_w
        y = (i // cols) * frame_h
        sheet.paste(frame_img, (x, y))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path)
