from sprite_cli.models import Frame, Transform


def apply_transform(frame: Frame, transform: Transform) -> Frame:
    if transform.type == "translate":
        return _translate(frame, transform.x or 0, transform.y or 0)
    elif transform.type == "flip":
        return _flip(frame, transform.axis or "horizontal")
    elif transform.type == "rotate":
        return _rotate(frame, transform.angle or 90)
    elif transform.type == "recolor":
        return _recolor(frame, transform.from_color or "", transform.to_color or "")
    elif transform.type == "scale":
        return _scale(frame, transform.factor or 1.0)
    else:
        raise ValueError(f"Unknown transform type: {transform.type}")


def _translate(frame: Frame, dx: int, dy: int) -> Frame:
    h = len(frame)
    w = max(len(row) for row in frame) if frame else 0
    new_frame: Frame = [[None] * w for _ in range(h)]
    for y, row in enumerate(frame):
        for x, pixel in enumerate(row):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                new_frame[ny][nx] = pixel
    return new_frame


def _flip(frame: Frame, axis: str) -> Frame:
    if axis == "horizontal":
        return [list(reversed(row)) for row in frame]
    else:
        return list(reversed([list(row) for row in frame]))


def _rotate(frame: Frame, angle: int) -> Frame:
    steps = (angle // 90) % 4
    result = [list(row) for row in frame]
    for _ in range(steps):
        rh = len(result)
        rw = max(len(row) for row in result) if result else 0
        rotated: Frame = [[None] * rh for _ in range(rw)]
        for y in range(rh):
            for x in range(len(result[y])):
                rotated[x][rh - 1 - y] = result[y][x]
        result = rotated
    return result


def _recolor(frame: Frame, from_color: str, to_color: str) -> Frame:
    return [
        [to_color if pixel == from_color else pixel for pixel in row]
        for row in frame
    ]


def _scale(frame: Frame, factor: float) -> Frame:
    h = len(frame)
    w = max(len(row) for row in frame) if frame else 0
    new_h = int(h * factor)
    new_w = int(w * factor)
    new_frame: Frame = [[None] * new_w for _ in range(new_h)]
    for ny in range(new_h):
        for nx in range(new_w):
            oy = min(int(ny / factor), h - 1)
            ox = min(int(nx / factor), w - 1)
            new_frame[ny][nx] = frame[oy][ox] if ox < len(frame[oy]) else None
    return new_frame
