"""Command-line interface for planning and executing anime scenes in Krita."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console

from krita_anime.compiler import Compilation, compile_plan
from krita_anime.deepseek import DEFAULT_BASE_URL, DEFAULT_MODEL, DeepSeekPlanner, load_api_key
from krita_anime.models import AnimePlan, CharacterPack
from krita_client import KritaClient
from krita_client.config import ClientConfig

app = typer.Typer(name="krita-anime", help="Plan and execute editable anime scenes in Krita.", no_args_is_help=True)
character_app = typer.Typer(help="Create and inspect character consistency packs.")
app.add_typer(character_app, name="character")
console = Console()


def _read_plan(path: Path) -> AnimePlan:
    return AnimePlan.model_validate_json(path.read_text(encoding="utf-8"))


def _command_data(compilation: Compilation) -> list[dict[str, Any]]:
    return [{"action": command.action, "params": command.params} for command in compilation.commands]


@app.command("validate")
def validate_plan(plan: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True)]) -> None:
    scene = _read_plan(plan)
    operations = sum(len(layer.operations) for layer in scene.layers)
    console.print(
        f"Valid: {scene.canvas.name} | {scene.canvas.width}x{scene.canvas.height} | "
        f"{len(scene.layers)} layer{'s' if len(scene.layers) != 1 else ''} | {operations} operations"
    )


@app.command("compile")
def compile_command(
    plan: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True)],
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    commands = _command_data(compile_plan(_read_plan(plan)))
    text = json.dumps(commands, ensure_ascii=False, indent=2)
    if output is None:
        console.print_json(text)
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text + "\n", encoding="utf-8")
    console.print(f"Wrote {len(commands)} commands to {output}")


@app.command("run")
def run_plan(
    plan: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True)],
    url: Annotated[str, typer.Option("--url", help="Krita plugin base URL")] = "http://127.0.0.1:5678",
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Compile without contacting Krita")] = False,
    report: Annotated[Path | None, typer.Option("--report")] = None,
) -> None:
    compilation = compile_plan(_read_plan(plan))
    commands = _command_data(compilation)
    if dry_run:
        console.print_json(json.dumps(commands, ensure_ascii=False))
        return

    results: list[dict[str, Any]] = []
    with KritaClient(ClientConfig(url=url)) as client:
        health = client.health()
        results.append({"action": "health", "result": health})
        for command in commands:
            params = dict(command["params"])
            if command["action"] == "save":
                target = Path(str(params["path"]))
                if not target.is_absolute():
                    target = (plan.parent / target).resolve()
                target.parent.mkdir(parents=True, exist_ok=True)
                params["path"] = str(target)
            result = client.call(command["action"], params)
            results.append({"action": command["action"], "result": result})

    if report is not None:
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    console.print(f"Executed {len(commands)} commands in Krita")


@app.command("plan")
def generate_plan(
    prompt: Annotated[str, typer.Argument(help="Text description of the scene")],
    output: Annotated[Path, typer.Option("--output", "-o")],
    character: Annotated[Path | None, typer.Option("--character")] = None,
    base_url: Annotated[str, typer.Option("--base-url")] = DEFAULT_BASE_URL,
    model: Annotated[str, typer.Option("--model")] = DEFAULT_MODEL,
) -> None:
    character_pack = None
    if character is not None:
        character_pack = CharacterPack.model_validate_json(character.read_text(encoding="utf-8"))
    planner = DeepSeekPlanner(api_key=load_api_key(Path.cwd()), base_url=base_url, model=model)
    scene = planner.create_plan(prompt, character_pack)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(scene.model_dump_json(indent=2) + "\n", encoding="utf-8")
    console.print(f"Wrote validated plan to {output}")


@character_app.command("init")
def init_character(
    output: Annotated[Path, typer.Argument(dir_okay=False)],
    character_id: Annotated[str, typer.Option("--id")] = "character",
) -> None:
    template = {
        "id": character_id,
        "anchors": {
            "face": "Describe jaw, nose, ears, and stable facial proportions",
            "eyes": "Describe eye shape, iris color, highlights, lashes, and spacing",
            "hair": "Describe silhouette, part, length, locks, and stable accessories",
            "signature": ["List at least one feature that must never drift"],
            "proportions": "Describe height in heads, shoulder width, and limb proportions",
        },
        "palette": {"skin": "#F2C6A8", "hair": "#202028", "eyes": "#7A4D2B"},
        "default_costume": "Describe the canonical costume from collar to footwear",
        "allowed_variations": ["pose", "expression", "scene lighting"],
        "references": [],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(template, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    console.print(f"Wrote character template to {output}")


if __name__ == "__main__":
    app()
