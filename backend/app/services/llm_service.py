from __future__ import annotations

from typing import Optional

from openai import OpenAI


class LLMService:
    """Thin client for an OpenAI-compatible chat completions API (including OpenRouter).

    The API key is never logged and never returned by the API.
    """

    def __init__(self, base_url: str, api_key: Optional[str], model: Optional[str]):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self._client: Optional[OpenAI] = None

    @property
    def is_enabled(self) -> bool:
        return bool(self.api_key and self.model)

    @property
    def client(self) -> OpenAI:
        if not self.is_enabled:
            raise RuntimeError(
                "LLM generation is not configured: set LLM_API_KEY and LLM_MODEL"
            )
        if self._client is None:
            self._client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        return self._client

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        if not self.is_enabled:
            raise RuntimeError("LLM generation is not configured")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        content = response.choices[0].message.content
        return content or ""