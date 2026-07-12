# Fine-Grained Anime Protocol

The customization adds four backward-compatible plugin actions to protocol `1.0.0`.

## `native_stroke`

Parameters: `preset`, `size`, `opacity`, and 2-4096 `{x,y,pressure}` document points. The plugin selects Krita's freehand tool, sends canvas events on the GUI thread, and varies native brush size with pressure. It never evaluates model-generated code.

## `import_svg_layer`

Parameters: `name`, inline `svg`, `opacity`, and `visible`. The plugin rejects scripts, external URLs, and SVG larger than 2 MB, then creates a Krita `shapelayer` and calls `addShapesFromSvg` so paths remain editable.

## `render_svg_paint_layer`

Parameters: `name`, inline `svg`, `opacity`, and `visible`. The plugin applies the same bounded SVG security policy, enforces the canvas dimension and 32-megapixel allocation limits, renders with Krita's embedded Qt SVG engine, and writes BGRA pixels to a dedicated `paintlayer`. This path requires an `RGBA/U8` document. It is the stable high-detail Bezier path for Krita 5/Qt5; it never imports an external bitmap or calls an image model.

## `create_storyboard`

Parameters: `name`, 1-64 in-canvas panels, border color/width, and gutter metadata. Each panel contains camera, action, dialogue, and notes. The plugin converts this bounded structure to an editable vector layer.

AnimePlan is a client-side planning protocol. It is validated before compilation and is not sent to Krita as executable text. See the generated schema through:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -c "from krita_anime.models import AnimePlan; print(AnimePlan.model_json_schema())"
```
