from unittest.mock import Mock

from krita_client.client import KritaClient


def client_with_sender() -> tuple[KritaClient, Mock]:
    client = KritaClient.__new__(KritaClient)
    sender = Mock(return_value={"status": "ok"})
    client._send = sender
    return client, sender


def test_native_stroke_validates_and_sends_pressure_points() -> None:
    client, sender = client_with_sender()

    client.native_stroke(
        points=[{"x": 10, "y": 20, "pressure": 0.3}, {"x": 30, "y": 40, "pressure": 0.8}],
        preset="Ink-3 Gpen",
        size=8.0,
        opacity=0.9,
    )

    sender.assert_called_once_with(
        "native_stroke",
        {
            "points": [{"x": 10.0, "y": 20.0, "pressure": 0.3}, {"x": 30.0, "y": 40.0, "pressure": 0.8}],
            "preset": "Ink-3 Gpen",
            "size": 8.0,
            "opacity": 0.9,
        },
    )


def test_import_svg_layer_sends_editable_vector_payload() -> None:
    client, sender = client_with_sender()

    client.import_svg_layer(name="hair-shape", svg="<svg></svg>", opacity=0.75, visible=False)

    sender.assert_called_once_with(
        "import_svg_layer",
        {"name": "hair-shape", "svg": "<svg></svg>", "opacity": 0.75, "visible": False},
    )


def test_create_storyboard_sends_panel_metadata() -> None:
    client, sender = client_with_sender()
    panels = [{"id": "p1", "x": 20, "y": 20, "width": 300, "height": 180, "action": "hero enters"}]

    client.create_storyboard(name="boards", panels=panels, border_color="#222222", border_width=4.0)

    sent = sender.call_args.args
    assert sent[0] == "create_storyboard"
    assert sent[1]["panels"][0]["camera"] == "medium shot"
    assert sent[1]["panels"][0]["action"] == "hero enters"
