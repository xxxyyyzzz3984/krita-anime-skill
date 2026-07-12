---
name: krita-finegrained-anime
description: Use when an agent must control Krita to draw layered, editable, fine-grained anime illustrations or storyboards; preserve a supplied character across poses, expressions, clothing, cameras, and scenes; use native brushes, stabilized pressure strokes, Bezier paths, or SVG vector layers; or turn a structured scene brief into bounded Krita actions.
---

# Krita Fine-Grained Anime

Use this skill as a model-neutral production protocol. The agent backend may be a text model, a vision-language model, or a local model; it must produce or edit an `AnimePlan` and let the local validator/compiler enforce the Krita action boundary. The skill does not call a hosted model and does not generate prose on the user's behalf.

## Choose The Path

- For a one-off illustration, author an `AnimePlan` directly from the brief.
- For a recurring or supplied character, create a character pack first and keep its anchors immutable.
- For a text-only backend, never claim to inspect an image. Use a supplied character pack or ask the user for observable traits.
- For a storyboard, create a `storyboard` layer before detailed paint/vector layers.

Read [references/plan-schema.md](references/plan-schema.md) before authoring JSON. Read [references/anime-workflow.md](references/anime-workflow.md) for consistency and finish criteria.

## Execute The Workflow

1. Check the bridge with `krita health` and `krita introspect capabilities`.
2. Create a character pack when identity must persist:

   ```powershell
   ./scripts/krita-anime.ps1 character init outputs/hero.json --id hero
   ```

3. Replace every template value with observable traits: face ratios, eye construction, hair silhouette, palette, proportions, signature items, and canonical costume.
4. Have the active agent backend author `outputs/scene.json` using the schema, or adapt `examples/anime-scene.json`.
5. Validate and compile before execution:

   ```powershell
   ./scripts/krita-anime.ps1 validate outputs/scene.json
   ./scripts/krita-anime.ps1 compile outputs/scene.json -o outputs/scene.commands.json
   ```

6. Execute with `./scripts/krita-anime.ps1 run outputs/scene.json --report outputs/scene.report.json`.
7. Inspect the layered `.kra`, exported preview, and report. Fix the smallest failing phase and rerun.

## Hard Invariants

- Preserve character-pack anchors exactly unless the brief explicitly changes an allowed variation.
- Keep storyboard, rough, lineart, color, vector, and notes in separate editable layers.
- Use pressure samples and the configured stabilizer for expressive linework; do not replace them with a single polygon.
- Use Bezier paths or SVG vector layers for clean curves, signs, motion lines, and repeated graphic shapes.
- Treat PNG/JPG as previews. The `.kra` and JSON plan are the editable source of truth.
- Never bypass schema validation or send free-form text as a Krita action.

## Failure Recovery

- If the bridge is unavailable, stop after validation/compile and report the exact health failure.
- If one operation fails, use the report and resume from a copied plan containing only remaining layers.
- If identity drifts, restore immutable anchors from the character pack before changing pose, costume, camera, or scene.
