import base64
import json
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import httpx

from app.settings import settings


class OllamaClient:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")

    async def health(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{self.base_url}/api/tags")
            r.raise_for_status()
            models = [m.get("name", "") for m in r.json().get("models", [])]
            required = [settings.chat_model, settings.embed_model, "gemma4:e4b"]
            missing = [m for m in required if m and not any(m in tag for tag in models)]
            return {"ok": True, "models": models, "missing_recommended": missing}

    async def embed(self, text: str, model: str | None = None) -> list[float]:
        model = model or settings.embed_model
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": model, "prompt": text},
            )
            r.raise_for_status()
            return r.json()["embedding"]

    @staticmethod
    def image_to_base64(path: Path) -> str:
        return base64.b64encode(path.read_bytes()).decode("ascii")

    async def chat(
        self,
        messages: list[dict[str, Any]],
        model: str,
        *,
        temperature: float = 0.7,
        top_p: float = 0.9,
        num_ctx: int | None = None,
        tools: list[dict[str, Any]] | None = None,
        stream: bool = False,
    ) -> str | AsyncIterator[str]:
        options: dict[str, Any] = {"temperature": temperature, "top_p": top_p}
        if num_ctx:
            options["num_ctx"] = num_ctx

        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": options,
        }
        if tools:
            payload["tools"] = tools

        if not stream:
            async with httpx.AsyncClient(timeout=300.0) as client:
                r = await client.post(f"{self.base_url}/api/chat", json=payload)
                r.raise_for_status()
                data = r.json()
                msg = data.get("message", {})
                content = msg.get("content", "")
                if msg.get("tool_calls"):
                    return json.dumps({"tool_calls": msg["tool_calls"]}, ensure_ascii=False)
                return content

        return self._stream_chat(payload)

    async def _stream_chat(self, payload: dict[str, Any]) -> AsyncIterator[str]:
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream(
                "POST", f"{self.base_url}/api/chat", json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    if chunk.get("done"):
                        break
                    content = chunk.get("message", {}).get("content", "")
                    if content:
                        yield content


ollama_client = OllamaClient()
