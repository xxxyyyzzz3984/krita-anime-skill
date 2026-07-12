---
name: krita-finegrained-anime
description: Use when an agent must control Krita to draw layered, editable, fine-grained anime illustrations or storyboards; preserve a supplied character across poses, expressions, clothing, cameras, and scenes; use native brushes, stabilized pressure strokes, Bezier paths, or SVG vector layers; or let a text-only model such as DeepSeek plan Krita artwork through strict JSON.
---

# Krita Fine-Grained Anime

Create an AnimePlan JSON, validate it locally, compile it to bounded Krita actions, and execute it through the customized plugin. Keep the `.kra` layered and editable; treat PNG/JPG as previews only.

## Choose The Path

- For an illustration with no recurring character, write the plan directly.
- For a recurring or supplied character, create a character pack first and keep its anchors immutable.
- For a text-only model, call `krita-anime plan`; never ask it to inspect an image. Translate the reference into a character pack first.
- For a storyboard, use a `storyboard` layer before detailed paint/vector layers.

Read [references/plan-schema.md](references/plan-schema.md) before manually authoring JSON. Read [references/anime-workflow.md](references/anime-workflow.md) for consistency and finish criteria.

## Execute The Workflow

1. Check the bridge with `krita health` and `krita introspect capabilities`.
2. Create a character pack when identity must persist:

   ```powershell
   ./scripts/krita-anime.ps1 character init outputs/hero.json --id hero
   ```

3. Replace every descriptive template value with observable traits. Record face ratios, eye construction, hair silhouette, palette, proportions, signature items, and canonical costume.
4. Generate a plan with DeepSeek or author JSON:

   ```powershell
   ./scripts/krita-anime.ps1 plan "Hero runs through a rainy station, three-quarter view" --character outputs/hero.json -o outputs/scene.json
   ```

5. Validate and inspect compiled actions before drawing:

   ```powershell
   ./scripts/krita-anime.ps1 validate outputs/scene.json
   ./scripts/krita-anime.ps1 compile outputs/scene.json -o outputs/scene.commands.json
   ```

6. Run against Krita and write an execution report:

   ```powershell
   ./scripts/krita-anime.ps1 run outputs/scene.json --report outputs/scene.report.json
   ```

7. Inspect the canvas. Revise only the weak phase, then rerun into a new numbered `.kra`; do not overwrite a useful iteration.

## Preserve Character Identity

Treat `anchors.face`, `anchors.eyes`, `anchors.hair`, `anchors.proportions`, `anchors.signature`, and palette values as immutable constraints. Change pose, expression, costume, lighting, camera, and setting only through `cast`. Keep signature features visible unless occlusion is explicitly required. Use the same character ID, anchor wording, and canonical colors in every shot.

When given only an image and the active model cannot see it, state that visual extraction needs a multimodal pass or human-authored manifest. Do not invent hidden traits and claim consistency.

## Build Editable Art

- Put loose construction in `rough` or `construction` paint layers.
- Put stabilized native brush strokes in `lineart`; use pressure taper at both ends.
- Put clean closed Bezier shapes in vector layers for hair masses, props, speed lines, panel borders, and graphics.
- Separate `flats`, `shadows`, `highlights`, and `effects` so revisions remain local.
- Use the storyboard vector action for panel borders, camera/action labels, dialogue, and notes.
- Save `.kra` before exporting a preview.

Use `assets/character-pack.template.json` as a starting asset. Use repository examples only as schema demonstrations, not as a universal visual style.

## Recover From Failures

- On `BRUSH_NOT_FOUND`, call `krita brush list` and replace the preset with an installed Krita preset.
- On native canvas-widget errors, bring the document view to the foreground, reset rotation/pan, and retry. Keep vector actions available as a deterministic fallback for precise lines.
- On validation errors, fix the JSON; do not bypass the schema with raw plugin calls.
- On partial execution, inspect the report and resume from a copied plan containing only remaining layers.
- Keep API keys in `DEEPSEEK_API_KEY`, `ds-api-key.txt`, or `ds-ap-key.txt`. Never print or embed them in plans.
