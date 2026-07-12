from __future__ import annotations

import importlib.util
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL_NAME = "krita-finegrained-anime"
CANONICAL = ROOT / "skills" / SKILL_NAME
MIRRORS = (
    ROOT / ".agents" / "skills" / SKILL_NAME,
    ROOT / ".claude" / "skills" / SKILL_NAME,
    ROOT / ".opencode" / "skills" / SKILL_NAME,
)
DEMO_FILES = (
    ROOT / "docs" / "demos" / "fine-lineart-scene.png",
    ROOT / "docs" / "demos" / "character-consistency-sheet.png",
    ROOT / "docs" / "demos" / "four-panel-storyboard.png",
)
KRA_FILES = tuple(path.with_suffix(".kra") for path in DEMO_FILES)


def _relative_files(directory: Path) -> set[Path]:
    return {path.relative_to(directory) for path in directory.rglob("*") if path.is_file()}


def _load_installer():
    script = ROOT / "scripts" / "install_agent_skill.py"
    spec = importlib.util.spec_from_file_location("install_agent_skill", script)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_skill_description_is_trigger_focused() -> None:
    lines = (CANONICAL / "SKILL.md").read_text(encoding="utf-8").splitlines()
    description = next(line for line in lines if line.startswith("description:"))
    assert description.startswith("description: Use when ")


def test_agent_skill_mirrors_are_byte_identical() -> None:
    expected_files = _relative_files(CANONICAL)
    assert expected_files

    for mirror in MIRRORS:
        assert mirror.is_dir(), f"missing agent layout: {mirror}"
        assert _relative_files(mirror) == expected_files
        for relative_path in expected_files:
            assert (mirror / relative_path).read_bytes() == (CANONICAL / relative_path).read_bytes()


def test_project_install_targets_all_supported_agents(tmp_path: Path) -> None:
    installer = _load_installer()
    expected = {
        "codex": tmp_path / ".agents" / "skills" / SKILL_NAME,
        "opencode": tmp_path / ".opencode" / "skills" / SKILL_NAME,
        "claude": tmp_path / ".claude" / "skills" / SKILL_NAME,
        "workbuddy": tmp_path / "skills" / SKILL_NAME,
    }

    for agent, destination in expected.items():
        installed = installer.install(
            source=CANONICAL,
            agent=agent,
            scope="project",
            project_root=tmp_path,
            home=tmp_path / "home",
            force=False,
        )
        assert installed == destination
        assert (destination / "SKILL.md").is_file()
        assert _relative_files(destination) == _relative_files(CANONICAL)


def test_user_install_targets_all_supported_agents(tmp_path: Path) -> None:
    installer = _load_installer()
    home = tmp_path / "home"
    expected = {
        "codex": home / ".agents" / "skills" / SKILL_NAME,
        "opencode": home / ".config" / "opencode" / "skills" / SKILL_NAME,
        "claude": home / ".claude" / "skills" / SKILL_NAME,
        "workbuddy": home / ".workbuddy" / "skills" / SKILL_NAME,
    }

    for agent, destination in expected.items():
        installed = installer.install(
            source=CANONICAL,
            agent=agent,
            scope="user",
            project_root=tmp_path,
            home=home,
            force=False,
        )
        assert installed == destination
        assert (destination / "SKILL.md").is_file()


def test_public_surface_is_model_neutral() -> None:
    public_files = (
        ROOT / "README.md",
        CANONICAL / "SKILL.md",
        ROOT / "src" / "krita_anime" / "cli.py",
    )
    for path in public_files:
        text = path.read_text(encoding="utf-8").lower()
        assert "deepseek" not in text, f"model-specific wording remains in {path}"

    cli_text = (ROOT / "src" / "krita_anime" / "cli.py").read_text(encoding="utf-8")
    assert '@app.command("plan")' not in cli_text
    assert not (ROOT / "src" / "krita_anime" / "deepseek.py").exists()


def test_readme_contains_skill_prompts_and_demo_gallery() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "## 如何调用 Skill" in readme
    assert readme.count("$krita-finegrained-anime") >= 3

    for demo in DEMO_FILES:
        assert demo.is_file(), f"missing demo image: {demo}"
        payload = demo.read_bytes()
        assert payload.startswith(b"\x89PNG\r\n\x1a\n")
        width = int.from_bytes(payload[16:20], "big")
        height = int.from_bytes(payload[20:24], "big")
        assert width >= 1600, f"demo is too narrow for fine anime detail: {demo}"
        assert height >= 1000, f"demo is too short for fine anime detail: {demo}"
        assert len(payload) >= 70_000, f"demo lacks the expected rendered detail: {demo}"
        relative = demo.relative_to(ROOT).as_posix()
        assert relative in readme

    for source in KRA_FILES:
        assert source.is_file(), f"missing Krita source: {source}"
        with zipfile.ZipFile(source) as archive:
            assert "maindoc.xml" in archive.namelist()
            document = archive.read("maindoc.xml")
            assert document.count(b'nodetype="paintlayer"') >= 3
        relative = source.relative_to(ROOT).as_posix()
        assert relative in readme
