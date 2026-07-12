"""Compile model-neutral anime plans into the Krita plugin protocol."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from krita_anime.geometry import stabilize_points
from krita_anime.models import AnimePlan, BezierPath, BrushStroke, Storyboard
from krita_anime.svg import render_svg

PHASE_ORDER = {
    "reference": 0,
    "rough": 1,
    "construction": 2,
    "lineart": 3,
    "flats": 4,
    "shadows": 5,
    "highlights": 6,
    "effects": 7,
    "notes": 8,
}


@dataclass(frozen=True)
class PluginCommand:
    action: str
    params: dict[str, Any]


@dataclass(frozen=True)
class Compilation:
    commands: list[PluginCommand]
    characters: dict[str, dict[str, Any]]
    cast: list[dict[str, Any]]


def compile_plan(plan: AnimePlan) -> Compilation:
    commands = [
        PluginCommand(
            "new_canvas",
            {
                "width": plan.canvas.width,
                "height": plan.canvas.height,
                "name": plan.canvas.name,
                "background": plan.canvas.background,
            },
        )
    ]

    for layer in sorted(plan.layers, key=lambda item: PHASE_ORDER[item.phase]):
        if layer.kind == "paint":
            commands.append(
                PluginCommand(
                    "create_layer",
                    {"name": layer.name, "layer_type": "paintlayer"},
                )
            )
            commands.append(PluginCommand("set_layer_opacity", {"name": layer.name, "opacity": layer.opacity}))
            commands.append(PluginCommand("set_layer_visibility", {"name": layer.name, "visible": layer.visible}))
            for operation in layer.operations:
                if not isinstance(operation, BrushStroke):
                    continue
                points = stabilize_points(operation.points, operation.stabilizer)
                commands.extend(
                    [
                        PluginCommand("set_color", {"color": operation.color}),
                        PluginCommand(
                            "set_brush",
                            {"preset": operation.preset, "size": operation.size, "opacity": operation.opacity},
                        ),
                        PluginCommand(
                            "native_stroke",
                            {
                                "preset": operation.preset,
                                "size": operation.size,
                                "opacity": operation.opacity,
                                "points": [point.model_dump() for point in points],
                            },
                        ),
                    ]
                )
        elif layer.kind == "vector":
            paths = [operation for operation in layer.operations if isinstance(operation, BezierPath)]
            commands.append(
                PluginCommand(
                    "import_svg_layer",
                    {
                        "name": layer.name,
                        "svg": render_svg(layer.name, plan.canvas.width, plan.canvas.height, paths),
                        "opacity": layer.opacity,
                        "visible": layer.visible,
                    },
                )
            )
        else:
            for operation in layer.operations:
                if isinstance(operation, Storyboard):
                    commands.append(
                        PluginCommand(
                            "create_storyboard",
                            {
                                "name": layer.name,
                                "panels": [panel.model_dump() for panel in operation.panels],
                                "gutter": operation.gutter,
                                "border_color": operation.border_color,
                                "border_width": operation.border_width,
                            },
                        )
                    )

    for target in plan.exports:
        commands.append(PluginCommand("save", {"path": target.path}))

    characters = {character.id: character.model_dump() for character in plan.characters}
    cast: list[dict[str, Any]] = []
    for instance in plan.cast:
        character = characters[instance.character_id]
        cast.append(
            {
                **instance.model_dump(),
                "costume": instance.costume or character["default_costume"],
                "anchors": character["anchors"],
                "palette": character["palette"],
            }
        )
    return Compilation(commands=commands, characters=characters, cast=cast)
