from unittest.mock import MagicMock, patch

from krita_mcp import server


def test_mcp_native_stroke_uses_pressure_points() -> None:
    client = MagicMock()
    client.native_stroke.return_value = {"status": "ok"}
    points = [{"x": 10, "y": 20, "pressure": 0.3}, {"x": 30, "y": 40, "pressure": 0.8}]

    with patch.object(server, "_get_client", return_value=client):
        result = server.krita_native_stroke(points=points, preset="Ink-3 Gpen", size=8.0)

    assert result == "Native stroke painted with 2 pressure points"
    client.native_stroke.assert_called_once_with(points=points, preset="Ink-3 Gpen", size=8.0, opacity=1.0)


def test_mcp_import_svg_layer_creates_vector_layer() -> None:
    client = MagicMock()
    client.import_svg_layer.return_value = {"status": "ok", "shape_count": 3}

    with patch.object(server, "_get_client", return_value=client):
        result = server.krita_import_svg_layer(name="hair", svg="<svg></svg>")

    assert result == "Created vector layer 'hair' with 3 shapes"


def test_mcp_create_storyboard_reports_panel_count() -> None:
    client = MagicMock()
    client.create_storyboard.return_value = {"status": "ok"}
    panels = [{"id": "1A", "x": 0, "y": 0, "width": 100, "height": 100, "action": "entrance"}]

    with patch.object(server, "_get_client", return_value=client):
        result = server.krita_create_storyboard(name="board", panels=panels)

    assert result == "Created storyboard 'board' with 1 panels"
