# AnimePlan Schema

Use `version: "1.0"` and reject undeclared fields.

## Root

- `canvas`: `width`, `height`, `name`, optional `background`.
- `characters`: reusable packs with `id`, `anchors`, `palette`, `default_costume`, optional variations/references.
- `cast`: per-scene `character_id`, `pose`, `expression`, optional costume and notes.
- `layers`: 1-100 editable layers.
- `exports`: 1-8 `kra`, `png`, `jpg`, or `webp` targets without `..` traversal.

## Layer Rules

Use phases in this order: `reference`, `rough`, `construction`, `lineart`, `flats`, `shadows`, `highlights`, `effects`, `notes`.

- `kind: "paint"` accepts only `brush_stroke`.
- `kind: "vector"` accepts only `bezier_path`.
- `kind: "storyboard"` accepts only `storyboard`.

## Operations

`brush_stroke` requires an installed `preset`, hex `color`, positive `size`, `opacity` in `(0,1]`, `stabilizer` in `[0,1]`, and at least two `{x,y,pressure}` points. Coordinates are document pixels. Taper lineart with lower endpoint pressure.

`bezier_path` requires `start` and one or more cubic segments containing `control1`, `control2`, and `end`. Use hex/`none` fill and stroke values, positive stroke width, optional closure and opacity.

`storyboard` contains 1-64 panels. Each panel needs `id`, in-canvas rectangle, `action`, and optional camera, dialogue, and notes. Panel rectangles must not exceed canvas bounds.

Run `krita-anime validate plan.json` as the authoritative schema check.
