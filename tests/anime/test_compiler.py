import pytest

from krita_anime.compiler import compile_plan
from krita_anime.models import AnimePlan

from .test_models import minimal_plan


def test_compile_orders_canvas_layer_brush_stroke_and_export() -> None:
    compilation = compile_plan(AnimePlan.model_validate(minimal_plan()))

    assert [command.action for command in compilation.commands] == [
        "new_canvas",
        "create_layer",
        "set_layer_opacity",
        "set_layer_visibility",
        "set_color",
        "set_brush",
        "native_stroke",
        "save",
    ]
    assert compilation.commands[6].params["points"][-1]["pressure"] == pytest.approx(0.9)
    assert compilation.characters["hero"]["anchors"]["hair"].startswith("short black bob")


def test_compile_vector_layer_imports_svg() -> None:
    payload = minimal_plan()
    payload["layers"] = [
        {
            "name": "speed-lines",
            "phase": "effects",
            "kind": "vector",
            "operations": [
                {
                    "op": "bezier_path",
                    "start": {"x": 10, "y": 20},
                    "segments": [
                        {
                            "control1": {"x": 20, "y": 20},
                            "control2": {"x": 30, "y": 20},
                            "end": {"x": 40, "y": 20},
                        }
                    ],
                    "stroke": "#000000",
                    "fill": "none",
                    "stroke_width": 2,
                }
            ],
        }
    ]

    compilation = compile_plan(AnimePlan.model_validate(payload))

    assert [command.action for command in compilation.commands] == [
        "new_canvas",
        "import_svg_layer",
        "save",
    ]
    assert "<svg" in compilation.commands[1].params["svg"]


def test_compile_uses_upstream_layer_type_and_applies_layer_state() -> None:
    payload = minimal_plan()
    payload["layers"][0]["opacity"] = 0.5
    payload["layers"][0]["visible"] = False

    compilation = compile_plan(AnimePlan.model_validate(payload))

    assert compilation.commands[1].params == {"name": "lineart", "layer_type": "paintlayer"}
    assert compilation.commands[2].action == "set_layer_opacity"
    assert compilation.commands[3].action == "set_layer_visibility"
