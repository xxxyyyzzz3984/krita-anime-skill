"""Cross-platform launcher for the Krita fine-grained anime CLI."""

# ruff: noqa: INP001 - standalone skill launcher, not an importable package

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

SKILL_ROOT = Path(__file__).resolve().parent.parent
REPOSITORY_MARKER = ".krita-finegrained-home"


def _is_repository(path: Path) -> bool:
    return (path / "src" / "krita_anime" / "cli.py").is_file()


def _repository_candidates() -> list[Path]:
    candidates: list[Path] = []
    configured = os.environ.get("KRITA_FINEGRAINED_HOME", "").strip()
    if configured:
        candidates.append(Path(configured).expanduser())

    marker = SKILL_ROOT / REPOSITORY_MARKER
    if marker.is_file():
        marked = marker.read_text(encoding="utf-8").strip()
        if marked:
            candidates.append(Path(marked).expanduser())

    candidates.extend((SKILL_ROOT, *SKILL_ROOT.parents))
    return candidates


def find_repository() -> Path | None:
    """Find a source checkout without assuming an agent-specific install path."""
    for candidate in _repository_candidates():
        resolved = candidate.resolve()
        if _is_repository(resolved):
            return resolved
    return None


def find_repository_python(repository: Path) -> Path | None:
    """Prefer a repository-hosted runtime on Windows or POSIX."""
    candidates = (
        repository / ".agent-runtime" / "Scripts" / "python.exe",
        repository / ".agent-runtime" / "bin" / "python",
        repository / ".venv" / "Scripts" / "python.exe",
        repository / ".venv" / "bin" / "python",
    )
    return next((candidate for candidate in candidates if candidate.is_file()), None)


def _run(command: Sequence[str], *, environment: dict[str, str]) -> int:
    completed = subprocess.run(command, env=environment, check=False)
    return completed.returncode


def main(arguments: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if arguments is None else arguments)
    environment = os.environ.copy()
    repository = find_repository()
    if repository is not None:
        source = str(repository / "src")
        existing = environment.get("PYTHONPATH", "")
        environment["PYTHONPATH"] = source if not existing else os.pathsep.join((source, existing))
        python = find_repository_python(repository) or Path(sys.executable)
        return _run((str(python), "-m", "krita_anime.cli", *args), environment=environment)

    if importlib.util.find_spec("krita_anime") is not None:
        return _run((sys.executable, "-m", "krita_anime.cli", *args), environment=environment)

    installed_command = shutil.which("krita-anime")
    if installed_command:
        return _run((installed_command, *args), environment=environment)

    message = (
        "Cannot locate the krita-anime CLI. Install krita-finegrained-cli or set "
        "KRITA_FINEGRAINED_HOME to the repository checkout."
    )
    print(message, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
