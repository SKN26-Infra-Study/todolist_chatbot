"""
애플리케이션 진입점.
실행 시 PYTHONPATH에 **프로젝트 루트**와 **`src`** 를 모두 넣는다 (`app` 패키지와 `todolist_chatbot` 패키지를 함께 찾기 위함).

예 (PowerShell, 루트에서):
  $root = "c:\\SKN26_ETC\\todolist_chatbot"
  $env:PYTHONPATH = "$root;$root\\src"
  python -m app.main

또는 프로젝트 루트에서:
  python -c "import runpy; runpy.run_path('app/main.py')"
"""

from __future__ import annotations


def main() -> None:
    # TODO: BotCore로 봇 기동 (구현 단계에서 연결)
    from todolist_chatbot.bot.core import BotCore

    _ = BotCore  # 임시 참조 — 스켈레톤 import 검증용
    raise SystemExit(
        "봇 기동 로직은 미구현입니다. 설계는 docs/ARCHITECTURE.md 를 참고하세요."
    )


if __name__ == "__main__":
    main()
