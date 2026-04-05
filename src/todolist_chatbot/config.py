"""환경 변수·봇 토큰·Supabase·OpenAI 등 설정."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

# --- OpenAI Chat Completions (intent / slot JSON) ---
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
OPENAI_CHAT_MODEL: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
# Azure OpenAI 등 호환 엔드포인트가 필요할 때만 설정 (미설정 시 공식 api.openai.com)
OPENAI_BASE_URL: str | None = os.getenv("OPENAI_BASE_URL") or None
