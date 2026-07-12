import json

import httpx
import pytest

from krita_anime.deepseek import DeepSeekPlanner, extract_json_object, load_api_key

from .test_models import minimal_plan


def test_load_api_key_prefers_environment(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    (tmp_path / "ds-api-key.txt").write_text("file-key", encoding="utf-8")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "env-key")

    assert load_api_key(tmp_path) == "env-key"


@pytest.mark.parametrize("filename", ["ds-api-key.txt", "ds-ap-key.txt"])
def test_load_api_key_supports_both_local_filenames(monkeypatch: pytest.MonkeyPatch, tmp_path, filename: str) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    (tmp_path / filename).write_text(" local-key\n", encoding="utf-8")

    assert load_api_key(tmp_path) == "local-key"


def test_extract_json_object_accepts_markdown_fence() -> None:
    text = 'Here is the plan:\n```json\n{"version": "1.0", "ok": true}\n```'

    assert extract_json_object(text)["ok"] is True


def test_planner_uses_openai_compatible_chat_completions() -> None:
    payload = minimal_plan()

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/chat/completions"
        body = json.loads(request.content)
        assert body["model"] == "deepseek-chat"
        assert body["response_format"] == {"type": "json_object"}
        assert request.headers["authorization"] == "Bearer test-key"
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(payload)}}]})

    with httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.deepseek.com") as client:
        plan = DeepSeekPlanner(api_key="test-key", client=client).create_plan("draw the hero running")

    assert plan.canvas.name == "shot-01"
    assert plan.cast[0].character_id == "hero"
