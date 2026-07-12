from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL_NAME = "krita-finegrained-anime"
CANONICAL = ROOT / "skills" / SKILL_NAME
MIRRORS = (
    ROOT / ".agents" / "skills" / SKILL_NAME,
    ROOT / ".claude" / "skills" / SKILL_NAME,
    ROOT / ".opencode" / "skills" / SKILL_NAME,
)


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
