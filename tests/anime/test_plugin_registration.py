from pathlib import Path

PLUGIN = Path(__file__).parents[2] / "krita-plugin" / "kritamcp" / "__init__.py"


def test_plugin_registers_all_anime_actions_and_capabilities() -> None:
    source = PLUGIN.read_text(encoding="utf-8")

    for action in ("native_stroke", "import_svg_layer", "create_storyboard"):
        assert f'"{action}": self.cmd_{action}' in source
        assert f'"{action}"' in source[source.index('"commands": [') : source.index("def do_POST")]


def test_new_paint_layer_becomes_active() -> None:
    source = PLUGIN.read_text(encoding="utf-8")
    create_layer = source[source.index("def cmd_create_layer") : source.index("def _find_node")]

    assert "doc.setActiveNode(layer)" in create_layer


def test_plugin_uses_qt5_qt6_compatibility_layer() -> None:
    source = PLUGIN.read_text(encoding="utf-8")
    compatibility = (PLUGIN.parent / "qt_compat.py").read_text(encoding="utf-8")

    assert "from PyQt5" not in source
    assert "from PyQt6" in compatibility
    assert "from PyQt5" in compatibility
