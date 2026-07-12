"""Synchronize the canonical skill into supported repository layouts."""

from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "krita-finegrained-anime"
CANONICAL = ROOT / "skills" / SKILL_NAME
MIRRORS = (
    ROOT / ".agents" / "skills" / SKILL_NAME,
    ROOT / ".claude" / "skills" / SKILL_NAME,
    ROOT / ".opencode" / "skills" / SKILL_NAME,
)


def directories_match(left: Path, right: Path) -> bool:
    if not left.is_dir() or not right.is_dir():
        return False
    comparison = filecmp.dircmp(left, right)
    if comparison.left_only or comparison.right_only or comparison.funny_files:
        return False
    if comparison.diff_files:
        return False
    return all(directories_match(left / name, right / name) for name in comparison.common_dirs)


def sync() -> None:
    if not CANONICAL.is_dir():
        message = f"Canonical skill not found: {CANONICAL}"
        raise FileNotFoundError(message)
    for mirror in MIRRORS:
        if mirror.exists():
            shutil.rmtree(mirror)
        mirror.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(CANONICAL, mirror)


def check() -> bool:
    return all(directories_match(CANONICAL, mirror) for mirror in MIRRORS)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Return a failure status instead of writing when mirrors differ.",
    )
    args = parser.parse_args()

    if args.check:
        if check():
            print("Agent skill layouts are synchronized.")
            return 0
        print("Agent skill layouts are out of date.")
        return 1

    sync()
    print("Synchronized: " + ", ".join(str(path) for path in MIRRORS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
