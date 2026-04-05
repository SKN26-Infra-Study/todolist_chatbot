"""환경 변수·봇 토큰·Supabase·OpenAI 등 설정."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# 패키지 위치 기준으로 프로젝트 루트의 .env 를 찾는다 (실행 cwd와 무관하게)
_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_ROOT / ".env")
load_dotenv()

# --- OpenAI Chat Completions (intent / slot JSON) ---
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
OPENAI_CHAT_MODEL: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
# Azure OpenAI 등 호환 엔드포인트가 필요할 때만 설정 (미설정 시 공식 api.openai.com)
OPENAI_BASE_URL: str | None = os.getenv("OPENAI_BASE_URL") or None
