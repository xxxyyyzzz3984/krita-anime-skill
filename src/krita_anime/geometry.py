"""Geometry helpers shared by offline compilation and the Krita plugin."""

from __future__ import annotations

from krita_anime.models import PressurePoint


def _catmull_rom(value0: float, value1: float, value2: float, value3: float, t: float) -> float:
    return 0.5 * (
        2 * value1
        + (-value0 + value2) * t
        + (2 * value0 - 5 * value1 + 4 * value2 - value3) * t * t
        + (-value0 + 3 * value1 - 3 * value2 + value3) * t * t * t
    )


def stabilize_points(points: list[PressurePoint], strength: float) -> list[PressurePoint]:
    """Densify and smooth a pressure stroke while preserving exact endpoints."""
    if len(points) < 2 or strength <= 0:
        return list(points)

    smoothed = list(points)
    for index in range(1, len(points) - 1):
        previous, current, following = points[index - 1 : index + 2]
        average_x = (previous.x + current.x + following.x) / 3
        average_y = (previous.y + current.y + following.y) / 3
        smoothed[index] = PressurePoint(
            x=current.x + (average_x - current.x) * strength,
            y=current.y + (average_y - current.y) * strength,
            pressure=current.pressure,
        )

    steps = 2 + round(strength * 6)
    result: list[PressurePoint] = []
    for index in range(len(smoothed) - 1):
        p0 = smoothed[max(0, index - 1)]
        p1 = smoothed[index]
        p2 = smoothed[index + 1]
        p3 = smoothed[min(len(smoothed) - 1, index + 2)]
        for step in range(steps):
            t = step / steps
            result.append(
                PressurePoint(
                    x=_catmull_rom(p0.x, p1.x, p2.x, p3.x, t),
                    y=_catmull_rom(p0.y, p1.y, p2.y, p3.y, t),
                    pressure=max(0.0, min(1.0, p1.pressure + (p2.pressure - p1.pressure) * t)),
                )
            )
    result.append(points[-1])
    result[0] = points[0]
    return result
