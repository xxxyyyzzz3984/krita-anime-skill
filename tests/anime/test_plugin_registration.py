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


def test_svg_import_uses_qbytearray_without_unsafe_string_probe() -> None:
    source = PLUGIN.read_text(encoding="utf-8")
    command = source[source.index("def cmd_import_svg_layer") : source.index("def cmd_create_storyboard")]

    assert 'layer.addShapesFromSvg(QByteArray(svg.encode("utf-8")))' in command
    assert "layer.addShapesFromSvg(svg)" not in command


def test_draw_shape_accepts_empty_active_paint_layer() -> None:
    source = PLUGIN.read_text(encoding="utf-8")
    start = source.index("def cmd_draw_shape")
    command = source[start : source.index("def cmd_get_canvas", start)]

    assert "if layer is None:" in command
    assert "if not layer:" not in command
