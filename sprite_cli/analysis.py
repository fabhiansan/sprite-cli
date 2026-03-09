from sprite_cli.models import SpriteDefinition


def sprite_canvas_size(sprite: SpriteDefinition) -> tuple[int, int]:
    width = 0
    height = 0

    for frames in sprite.frames.values():
        for frame in frames:
            height = max(height, len(frame))
            width = max(width, max((len(row) for row in frame), default=0))

    return width, height


def analyze_sprite(sprite: SpriteDefinition) -> dict:
    canvas_width, canvas_height = sprite_canvas_size(sprite)
    return {
        "name": sprite.name,
        "canvas": {
            "width": canvas_width,
            "height": canvas_height,
        },
        "render_size": sprite.size,
        "palette_count": len(sprite.palette),
        "frame_sets": {
            name: len(frames)
            for name, frames in sprite.frames.items()
        },
        "animations": {
            name: {
                "base": animation.base,
                "fps": animation.fps,
                "loop": animation.loop,
                "steps": len(animation.transforms),
            }
            for name, animation in sprite.animations.items()
        },
        "anchors": {
            name: {
                "x": anchor.x,
                "y": anchor.y,
                "normalized": {
                    "x": (anchor.x / canvas_width) if canvas_width else 0,
                    "y": (anchor.y / canvas_height) if canvas_height else 0,
                },
            }
            for name, anchor in sprite.anchors.items()
        },
        "regions": {
            name: {
                "x": region.x,
                "y": region.y,
                "w": region.w,
                "h": region.h,
                "normalized": {
                    "x": (region.x / canvas_width) if canvas_width else 0,
                    "y": (region.y / canvas_height) if canvas_height else 0,
                    "w": (region.w / canvas_width) if canvas_width else 0,
                    "h": (region.h / canvas_height) if canvas_height else 0,
                },
            }
            for name, region in sprite.regions.items()
        },
    }
