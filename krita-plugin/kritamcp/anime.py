"""Pure helpers for the fine-grained anime plugin actions."""

from __future__ import annotations

from html import escape
from typing import Any
from xml.etree import ElementTree as ET


def normalize_native_points(points: list[dict[str, Any]]) -> list[dict[str, float]]:
    if len(points) < 2:
        message = "native stroke needs at least two points"
        raise ValueError(message)
    normalized: list[dict[str, float]] = []
    for index, point in enumerate(points):
        try:
            x = float(point["x"])
            y = float(point["y"])
            pressure = float(point.get("pressure", 1.0))
        except (KeyError, TypeError, ValueError) as error:
            message = f"invalid native stroke point at index {index}"
            raise ValueError(message) from error
        if not 0.0 <= pressure <= 1.0:
            message = f"pressure at index {index} must be between 0 and 1"
            raise ValueError(message)
        normalized.append({"x": x, "y": y, "pressure": pressure})
    return normalized


def is_safe_inline_svg(value: str) -> bool:
    """Accept inline SVG XML while rejecting executable or external content."""
    try:
        root = ET.fromstring(value)  # noqa: S314 - caller caps SVG payload at 2 MB
    except ET.ParseError:
        return False
    if root.tag.rsplit("}", 1)[-1].lower() != "svg":
        return False
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1].lower() in {"script", "style"}:
            return False
        for attribute, raw_value in element.attrib.items():
            name = attribute.rsplit("}", 1)[-1].lower()
            lowered = raw_value.strip().lower()
            has_external_scheme = any(scheme in lowered for scheme in ("javascript:", "file://", "http://", "https://"))
            if name.startswith("on") or has_external_scheme or (name == "href" and not lowered.startswith("#")):
                return False
    return True


def validate_svg_render_target(
    width: int,
    height: int,
    color_model: str,
    color_depth: str,
    *,
    max_dimension: int = 8192,
    max_pixels: int = 32_000_000,
) -> None:
    """Reject targets that cannot safely receive a full-canvas BGRA8 buffer."""
    if width <= 0 or height <= 0 or width > max_dimension or height > max_dimension:
        message = f"SVG render dimensions must be between 1 and {max_dimension} pixels"
        raise ValueError(message)
    if width * height > max_pixels:
        message = f"SVG render exceeds the {max_pixels} pixel budget"
        raise ValueError(message)
    if color_model != "RGBA" or color_depth != "U8":
        message = "SVG paint rendering requires an RGBA/U8 document"
        raise ValueError(message)


def storyboard_svg(
    width: int,
    height: int,
    panels: list[dict[str, Any]],
    border_color: str,
    border_width: float,
) -> str:
    elements: list[str] = []
    for panel in panels:
        x, y = int(panel["x"]), int(panel["y"])
        panel_width, panel_height = int(panel["width"]), int(panel["height"])
        elements.append(
            f'<g aria-label="{escape(str(panel["id"]), quote=True)}">'
            f'<rect x="{x}" y="{y}" width="{panel_width}" height="{panel_height}" '
            f'fill="white" stroke="{border_color}" stroke-width="{border_width:g}"/>'
        )
        labels = [
            ("CAM", panel.get("camera", "medium shot")),
            ("ACT", panel.get("action", "")),
            ("DIA", panel.get("dialogue", "")),
            ("NOTE", panel.get("notes", "")),
        ]
        line_y = y + 22
        for prefix, value in labels:
            if not value:
                continue
            text = escape(f"{prefix}: {value}")
            elements.append(f'<text x="{x + 10}" y="{line_y}" font-size="13" fill="#333333">{text}</text>')
            line_y += 18
        elements.append("</g>")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">' + "".join(elements) + "</svg>"
    )
