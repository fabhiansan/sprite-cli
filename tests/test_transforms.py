from sprite_cli.models import Frame, Transform
from sprite_cli.transforms import apply_transform


def test_translate():
    frame: Frame = [
        [None, None, None],
        [None, "r", None],
        [None, None, None],
    ]
    t = Transform(type="translate", x=1, y=0)
    result = apply_transform(frame, t)
    assert result[1][2] == "r"
    assert result[1][1] is None


def test_translate_up():
    frame: Frame = [
        [None, None, None],
        [None, "r", None],
        [None, None, None],
    ]
    t = Transform(type="translate", x=0, y=-1)
    result = apply_transform(frame, t)
    assert result[0][1] == "r"
    assert result[1][1] is None


def test_flip_horizontal():
    frame: Frame = [
        ["r", "g"],
        ["b", "w"],
    ]
    t = Transform(type="flip", axis="horizontal")
    result = apply_transform(frame, t)
    assert result == [["g", "r"], ["w", "b"]]


def test_flip_vertical():
    frame: Frame = [
        ["r", "g"],
        ["b", "w"],
    ]
    t = Transform(type="flip", axis="vertical")
    result = apply_transform(frame, t)
    assert result == [["b", "w"], ["r", "g"]]


def test_rotate_90():
    frame: Frame = [
        ["r", "g"],
        ["b", "w"],
    ]
    t = Transform(type="rotate", angle=90)
    result = apply_transform(frame, t)
    assert result == [["b", "r"], ["w", "g"]]


def test_recolor():
    frame: Frame = [
        ["r", "g"],
        ["r", "b"],
    ]
    t = Transform(type="recolor", from_color="r", to_color="g")
    result = apply_transform(frame, t)
    assert result == [["g", "g"], ["g", "b"]]


def test_scale():
    frame: Frame = [
        ["r", "g"],
        ["b", "w"],
    ]
    t = Transform(type="scale", factor=2.0)
    result = apply_transform(frame, t)
    assert len(result) == 4
    assert len(result[0]) == 4
    assert result[0][0] == "r"
    assert result[0][1] == "r"
    assert result[1][0] == "r"
    assert result[1][1] == "r"
