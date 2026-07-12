"""Deterministic SVG generation for Krita vector layers."""

from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from krita_anime.models import BezierPath


def _number(value: float) -> str:
    return f"{value:g}"


def render_svg(name: str, width: int, height: int, paths: list[BezierPath]) -> str:
    path_elements: list[str] = []
    for path in paths:
        commands = [f"M {_number(path.start.x)} {_number(path.start.y)}"]
        for segment in path.segments:
            commands.append(
                "C "
                f"{_number(segment.control1.x)} {_number(segment.control1.y)} "
                f"{_number(segment.control2.x)} {_number(segment.control2.y)} "
                f"{_number(segment.end.x)} {_number(segment.end.y)}"
            )
        if path.closed:
            commands.append("Z")
        path_elements.append(
            '<path d="'
            + " ".join(commands)
            + f'" stroke="{path.stroke}" fill="{path.fill}" '
            + f'stroke-width="{_number(path.stroke_width)}" opacity="{_number(path.opacity)}" '
            + 'stroke-linecap="round" stroke-linejoin="round"/>'
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" aria-label="{escape(name, quote=True)}">' + "".join(path_elements) + "</svg>"
    )
