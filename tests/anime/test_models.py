import pytest
from pydantic import ValidationError

from krita_anime.models import AnimePlan


def minimal_plan() -> dict:
    return {
        "version": "1.0",
        "canvas": {"width": 1280, "height": 720, "name": "shot-01"},
        "characters": [
            {
                "id": "hero",
                "anchors": {
                    "face": "soft V jaw, small nose",
                    "eyes": "large amber eyes with two highlights",
                    "hair": "short black bob with a red left-side clip",
                    "signature": ["red hair clip"],
                },
                "palette": {"hair": "#171820", "eyes": "#D98A31"},
                "default_costume": "navy school uniform",
            }
        ],
        "cast": [
            {
                "character_id": "hero",
                "pose": "three-quarter running pose",
                "expression": "determined",
                "costume": "rain jacket over the default uniform",
            }
        ],
        "layers": [
            {
                "name": "lineart",
                "phase": "lineart",
                "kind": "paint",
                "operations": [
                    {
                        "op": "brush_stroke",
                        "preset": "Basic-5 Size",
                        "color": "#202028",
                        "size": 7.5,
                        "stabilizer": 0.65,
                        "points": [
                            {"x": 100, "y": 120, "pressure": 0.25},
                            {"x": 240, "y": 180, "pressure": 0.9},
                        ],
                    }
                ],
            }
        ],
        "exports": [{"path": "outputs/shot-01.kra", "format": "kra"}],
    }


def test_anime_plan_accepts_character_and_pressure_stroke() -> None:
    plan = AnimePlan.model_validate(minimal_plan())

    assert plan.cast[0].character_id == "hero"
    assert plan.layers[0].operations[0].points[1].pressure == 0.9


def test_anime_plan_rejects_unknown_fields() -> None:
    payload = minimal_plan()
    payload["surprise"] = True

    with pytest.raises(ValidationError, match="surprise"):
        AnimePlan.model_validate(payload)


def test_anime_plan_rejects_unknown_character_reference() -> None:
    payload = minimal_plan()
    payload["cast"][0]["character_id"] = "missing"

    with pytest.raises(ValidationError, match="missing"):
        AnimePlan.model_validate(payload)


def test_anime_plan_limits_total_operations() -> None:
    payload = minimal_plan()
    operation = payload["layers"][0]["operations"][0]
    payload["layers"][0]["operations"] = [operation] * 2001

    with pytest.raises(ValidationError, match="2000"):
        AnimePlan.model_validate(payload)
