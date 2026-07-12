"""Live health and optional drawing smoke test for a running Krita bridge."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from krita_anime.compiler import compile_plan
from krita_anime.models import AnimePlan
from krita_client import KritaClient
from krita_client.config import ClientConfig


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:5678")
    parser.add_argument("--health-only", action="store_true")
    parser.add_argument("--plan", type=Path, default=Path("examples/storyboard.json"))
    parser.add_argument("--report", type=Path, default=Path("outputs/live-smoke-report.json"))
    args = parser.parse_args()

    results = []
    with KritaClient(ClientConfig(url=args.url)) as client:
        health = client.health()
        print(json.dumps(health, ensure_ascii=False))
        if args.health_only:
            return 0
        scene = AnimePlan.model_validate_json(args.plan.read_text(encoding="utf-8"))
        for command in compile_plan(scene).commands:
            result = client.call(command.action, command.params)
            results.append({"action": command.action, "result": result})

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
