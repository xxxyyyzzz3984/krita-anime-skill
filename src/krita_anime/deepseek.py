"""DeepSeek adapter for generating strict AnimePlan JSON from text."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import httpx

from krita_anime.models import AnimePlan, CharacterPack

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"


def load_api_key(directory: Path | None = None) -> str:
    value = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if value:
        return value
    root = directory or Path.cwd()
    for filename in ("ds-api-key.txt", "ds-ap-key.txt"):
        path = root / filename
        if path.is_file():
            value = path.read_text(encoding="utf-8").strip()
            if value:
                return value
    message = "DeepSeek API key not found in DEEPSEEK_API_KEY, ds-api-key.txt, or ds-ap-key.txt"
    raise RuntimeError(message)


def extract_json_object(text: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()
    for index, character in enumerate(text):
        if character != "{":
            continue
        try:
            value, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    message = "DeepSeek response did not contain a JSON object"
    raise ValueError(message)


class DeepSeekPlanner:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        client: httpx.Client | None = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.client = client

    def _messages(self, prompt: str, character: CharacterPack | None) -> list[dict[str, str]]:
        schema = json.dumps(AnimePlan.model_json_schema(), ensure_ascii=False, separators=(",", ":"))
        system = (
            "You are a production anime scene planner for Krita. Return one JSON object only. "
            "Use editable layers in phase order and concrete brush points or Bezier paths. "
            "Preserve every immutable character anchor exactly while changing only requested pose, costume, "
            "expression, "
            "camera, and setting. The JSON must validate against this schema: " + schema
        )
        user = prompt
        if character is not None:
            user += "\nCharacter pack (copy it into characters and reference its id from cast):\n"
            user += character.model_dump_json()
        return [{"role": "system", "content": system}, {"role": "user", "content": user}]

    def create_plan(self, prompt: str, character: CharacterPack | None = None) -> AnimePlan:
        payload = {
            "model": self.model,
            "messages": self._messages(prompt, character),
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        owns_client = self.client is None
        client = self.client or httpx.Client(base_url=self.base_url, timeout=120.0)
        try:
            response = client.post("/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return AnimePlan.model_validate(extract_json_object(content))
        except (KeyError, IndexError, TypeError) as error:
            message = "DeepSeek response has no assistant message content"
            raise ValueError(message) from error
        finally:
            if owns_client:
                client.close()
