"""
LLMInterpreter: 자연어 → intent + slots JSON 파싱.
유일한(또는 주된) 생성형 LLM 호출 지점. DB/도구 호출 없음.

OpenAI Chat Completions API — 기본 모델 gpt-4o-mini (`config.OPENAI_CHAT_MODEL`).
"""

from __future__ import annotations

from typing import Any

from openai import OpenAI

from todolist_chatbot import config


class LLMInterpreter:
    """구조화된 해석은 이후 Pydantic 등으로 검증·파싱하면 된다."""

    def __init__(
        self,
        *,
        client: OpenAI | None = None,
        model: str | None = None,
    ) -> None:
        if client is not None:
            self._client = client
        else:
            if not config.OPENAI_API_KEY:
                raise ValueError(
                    "OPENAI_API_KEY 가 설정되지 않았습니다 (.env 또는 환경 변수)."
                )
            kwargs: dict[str, Any] = {"api_key": config.OPENAI_API_KEY}
            if config.OPENAI_BASE_URL:
                kwargs["base_url"] = config.OPENAI_BASE_URL
            self._client = OpenAI(**kwargs)
        self._model = model or config.OPENAI_CHAT_MODEL

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.2,
        top_p: float = 1.0,
        max_tokens: int = 1024,
        stream: bool = False,
    ) -> str:
        """대화 완성 한 번 호출 — DialogueManager가 system/user 메시지를 조합해 넘긴다."""
        completion = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stream=stream,
        )
        choice = completion.choices[0].message
        return (choice.content or "").strip()

    def interpret_raw(self, user_text: str, system_prompt: str) -> str:
        """intent/slot JSON용 — 구현 시 system_prompt에 스키마를 넣는다."""
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ]
        return self.chat(messages)
