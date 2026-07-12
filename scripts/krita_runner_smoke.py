"""Run inside kritarunner to exercise the plugin against the real Krita API."""

from __future__ import annotations

import json
import os
import sys
import traceback
from pathlib import Path


def smoke() -> None:
    plugin_root = os.environ["KRITA_FINEGRAINED_PLUGIN_ROOT"]
    output_dir = Path(os.environ["KRITA_FINEGRAINED_OUTPUT_DIR"])
    output_dir.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, plugin_root)

    report = {"status": "error", "results": []}
    report_path = output_dir / "krita-runner-report.json"
    try:
        from krita import Krita
        from kritamcp import KritaMCPExtension
        from kritamcp.qt_compat import QT_MAJOR

        app = Krita.instance()
        document = app.createDocument(800, 600, "krita-runner-smoke", "RGBA", "U8", "", 120.0)
        app.setActiveDocument(document)
        background = document.createNode("background", "paintlayer")
        document.rootNode().addChildNode(background, None)
        document.setActiveNode(background)

        extension = KritaMCPExtension(app)
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">'
            '<path d="M 100 300 C 220 80 580 80 700 300" stroke="#202028" fill="none" stroke-width="8"/>'
            "</svg>"
        )
        vector_result = extension.cmd_import_svg_layer(
            {"name": "bezier-line", "svg": svg, "opacity": 1.0, "visible": True}
        )
        report["results"].append({"action": "import_svg_layer", "result": vector_result})

        storyboard_result = extension.cmd_create_storyboard(
            {
                "name": "storyboard",
                "panels": [
                    {
                        "id": "1A",
                        "x": 40,
                        "y": 40,
                        "width": 300,
                        "height": 180,
                        "camera": "medium shot",
                        "action": "hero enters",
                        "dialogue": "Hello",
                        "notes": "identity anchors visible",
                    }
                ],
                "border_color": "#202020",
                "border_width": 4.0,
            }
        )
        report["results"].append({"action": "create_storyboard", "result": storyboard_result})

        paint = document.createNode("native-ink", "paintlayer")
        document.rootNode().addChildNode(paint, None)
        document.setActiveNode(paint)
        native_result = extension.cmd_native_stroke(
            {
                "preset": "Basic-5 Size",
                "size": 18.0,
                "opacity": 1.0,
                "points": [
                    {"x": 180, "y": 420, "pressure": 0.2},
                    {"x": 400, "y": 360, "pressure": 0.9},
                    {"x": 620, "y": 420, "pressure": 0.2},
                ],
            }
        )
        report["results"].append({"action": "native_stroke", "result": native_result})

        output_path = output_dir / "krita-runner-smoke.kra"
        save_result = extension.cmd_save({"path": str(output_path)})
        report["results"].append({"action": "save", "result": save_result})
        report.update(
            {
                "status": "ok",
                "qt_major": QT_MAJOR,
                "krita_version": app.version(),
                "layers": [node.name() for node in document.rootNode().childNodes()],
            }
        )
    except Exception:
        report["traceback"] = traceback.format_exc()
    finally:
        with report_path.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2)
