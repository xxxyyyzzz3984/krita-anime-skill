"""Install the bundled Krita anime skill for a supported coding agent."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "krita-finegrained-anime"
DEFAULT_SOURCE = ROOT / "skills" / SKILL_NAME
SUPPORTED_AGENTS = ("codex", "opencode", "claude", "workbuddy")
PROJECT_SKILL_DIRS = {
    "codex": Path(".agents/skills"),
    "opencode": Path(".opencode/skills"),
    "claude": Path(".claude/skills"),
    "workbuddy": Path("skills"),
}
USER_SKILL_DIRS = {
    "codex": Path(".codex/skills"),
    "opencode": Path(".config/opencode/skills"),
    "claude": Path(".claude/skills"),
    "workbuddy": Path(".workbuddy/skills"),
}


def repository_for_source(source: Path) -> Path | None:
    """Return the containing checkout when installing from a full repository."""
    for candidate in (source, *source.parents):
        if (candidate / "src" / "krita_anime" / "cli.py").is_file():
            return candidate
    return None


def destination_for(*, agent: str, scope: str, project_root: Path, home: Path) -> Path:
    if agent not in SUPPORTED_AGENTS:
        message = f"Unsupported agent: {agent}"
        raise ValueError(message)
    if scope == "project":
        return project_root / PROJECT_SKILL_DIRS[agent] / SKILL_NAME
    if scope == "user":
        return home / USER_SKILL_DIRS[agent] / SKILL_NAME
    message = f"Unsupported scope: {scope}"
    raise ValueError(message)


def install(
    *,
    source: Path,
    agent: str,
    scope: str,
    project_root: Path,
    home: Path,
    force: bool,
) -> Path:
    source = source.resolve()
    if not (source / "SKILL.md").is_file():
        message = f"Skill source is invalid: {source}"
        raise FileNotFoundError(message)

    destination = destination_for(
        agent=agent,
        scope=scope,
        project_root=project_root.resolve(),
        home=home.resolve(),
    )
    if destination.exists():
        if not force:
            message = f"Destination exists: {destination}. Re-run with --force to replace it."
            raise FileExistsError(message)
        shutil.rmtree(destination)

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    if scope == "user":
        repository = repository_for_source(source)
        if repository is not None:
            marker = destination / ".krita-finegrained-home"
            marker.write_text(f"{repository}\n", encoding="utf-8")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--agent",
        choices=(*SUPPORTED_AGENTS, "all"),
        default="codex",
    )
    parser.add_argument("--scope", choices=("project", "user"), default="user")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    agents = SUPPORTED_AGENTS if args.agent == "all" else (args.agent,)
    for agent in agents:
        destination = install(
            source=args.source,
            agent=agent,
            scope=args.scope,
            project_root=args.project_root,
            home=args.home,
            force=args.force,
        )
        print(f"Installed {agent}: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
