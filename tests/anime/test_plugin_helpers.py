import importlib.util
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).parents[2] / "krita-plugin" / "kritamcp" / "anime.py"
SPEC = importlib.util.spec_from_file_location("kritamcp_anime_helpers", MODULE_PATH)
assert SPEC
assert SPEC.loader
anime = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(anime)


def test_storyboard_svg_contains_panels_and_xml_escaped_notes() -> None:
    svg = anime.storyboard_svg(
        800,
        600,
        [
            {
                "id": "p1",
                "x": 20,
                "y": 30,
                "width": 300,
                "height": 180,
                "camera": "close-up",
                "action": "hero < wakes",
                "dialogue": "Go & now",
                "notes": "",
            }
        ],
        "#202020",
        4,
    )

    assert '<rect x="20" y="30" width="300" height="180"' in svg
    assert "hero &lt; wakes" in svg
    assert "Go &amp; now" in svg


def test_normalize_native_points_rejects_invalid_pressure() -> None:
    with pytest.raises(ValueError, match="pressure"):
        anime.normalize_native_points([{"x": 1, "y": 2, "pressure": 2.0}, {"x": 3, "y": 4}])


def test_inline_svg_security_allows_namespace_only() -> None:
    valid = '<svg xmlns="http://www.w3.org/2000/svg"><path d="M 0 0 L 1 1"/></svg>'
    assert anime.is_safe_inline_svg(valid)

    external = '<svg xmlns="http://www.w3.org/2000/svg"><image href="https://example.com/a.png"/></svg>'
    assert not anime.is_safe_inline_svg(external)
