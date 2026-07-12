import json

from typer.testing import CliRunner

from krita_anime.cli import app

from .test_models import minimal_plan

runner = CliRunner()


def test_validate_prints_plan_summary(tmp_path) -> None:
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(minimal_plan()), encoding="utf-8")

    result = runner.invoke(app, ["validate", str(plan_path)])

    assert result.exit_code == 0
    assert "shot-01" in result.stdout
    assert "1 layer" in result.stdout


def test_compile_writes_replayable_command_json(tmp_path) -> None:
    plan_path = tmp_path / "plan.json"
    output_path = tmp_path / "commands.json"
    plan_path.write_text(json.dumps(minimal_plan()), encoding="utf-8")

    result = runner.invoke(app, ["compile", str(plan_path), "--output", str(output_path)])

    assert result.exit_code == 0
    commands = json.loads(output_path.read_text(encoding="utf-8"))
    assert commands[0]["action"] == "new_canvas"
    assert commands[-1] == {"action": "save", "params": {"path": "outputs/shot-01.kra"}}


def test_character_init_creates_text_model_manifest(tmp_path) -> None:
    output_path = tmp_path / "hero.json"

    result = runner.invoke(app, ["character", "init", str(output_path), "--id", "hero"])

    assert result.exit_code == 0
    manifest = json.loads(output_path.read_text(encoding="utf-8"))
    assert manifest["id"] == "hero"
    assert set(manifest["anchors"]) >= {"face", "eyes", "hair", "signature"}
