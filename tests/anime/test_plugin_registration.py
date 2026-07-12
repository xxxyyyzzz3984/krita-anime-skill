from pathlib import Path

PLUGIN = Path(__file__).parents[2] / "krita-plugin" / "kritamcp" / "__init__.py"


def test_plugin_registers_all_anime_actions_and_capabilities() -> None:
    source = PLUGIN.read_text(encoding="utf-8")

    for action in ("native_stroke", "import_svg_layer", "render_svg_paint_layer", "create_storyboard"):
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


def test_svg_import_blocks_known_crashing_qt5_binding() -> None:
    source = PLUGIN.read_text(encoding="utf-8")
    start = source.index("def cmd_import_svg_layer")
    command = source[start : source.index("def cmd_create_storyboard", start)]

    guard = command.index("if QT_MAJOR < 6:")
    native_call = command.index("layer.addShapesFromSvg")
    assert guard < native_call
    assert 'code="UNSUPPORTED_OPERATION"' in command


def test_svg_paint_render_uses_qt_renderer_and_krita_paint_layer() -> None:
    source = PLUGIN.read_text(encoding="utf-8")
    start = source.index("def cmd_render_svg_paint_layer")
    command = source[start : source.index("def cmd_create_storyboard", start)]

    assert 'doc.createNode(name, "paintlayer")' in command
    assert 'QSvgRenderer(QByteArray(svg.encode("utf-8")))' in command
    assert "QPainter(image)" in command
    assert "validate_svg_render_target" in command
    assert "if image.isNull():" in command
    assert "layer.setPixelData" in command
    assert '"engine": "krita-qt-svg"' in command
