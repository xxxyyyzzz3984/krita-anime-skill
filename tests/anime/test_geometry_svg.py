from krita_anime.geometry import stabilize_points
from krita_anime.models import BezierPath, PressurePoint
from krita_anime.svg import render_svg


def test_stabilizer_preserves_endpoints_and_pressure() -> None:
    points = [
        PressurePoint(x=0, y=0, pressure=0.2),
        PressurePoint(x=40, y=80, pressure=0.8),
        PressurePoint(x=100, y=20, pressure=0.4),
    ]

    result = stabilize_points(points, strength=0.8)

    assert (result[0].x, result[0].y, result[0].pressure) == (0, 0, 0.2)
    assert (result[-1].x, result[-1].y, result[-1].pressure) == (100, 20, 0.4)
    assert len(result) > len(points)


def test_render_svg_emits_cubic_path_and_escapes_layer_name() -> None:
    path = BezierPath.model_validate(
        {
            "op": "bezier_path",
            "start": {"x": 10, "y": 20},
            "segments": [
                {
                    "control1": {"x": 30, "y": 0},
                    "control2": {"x": 70, "y": 100},
                    "end": {"x": 90, "y": 20},
                }
            ],
            "stroke": "#112233",
            "fill": "none",
            "stroke_width": 3,
        }
    )

    svg = render_svg("ink & shine", 100, 120, [path])

    assert 'aria-label="ink &amp; shine"' in svg
    assert 'd="M 10 20 C 30 0 70 100 90 20"' in svg
    assert 'stroke="#112233"' in svg
