"""
OpenAI(gpt-4o-mini) 연결 및 간단 대화 스모크 테스트.

실행 위치: 프로젝트 루트에서 권장.

  pip install -r requirements.txt
  # .env 에 OPENAI_API_KEY 설정

  python scripts/test_openai.py              # 1회 핑 + (선택) intent JSON 1회
  python scripts/test_openai.py --repl       # 터미널에서 여러 턴 대화
  python scripts/test_openai.py --intent-only

환경은 todolist_chatbot.config 가 루트 .env 를 읽는다.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# 프로젝트 루트 · src 를 path 에 넣어 패키지 import 가능하게
_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from todolist_chatbot.llm.interpreter import LLMInterpreter

# 짧은 intent 테스트용 시스템 프롬프트 (전체는 docs/ARCHITECTURE.md §8.3)
_INTENT_SYSTEM = """당신은 Discord Todo 봇의 의도 분석기입니다. 출력은 JSON 한 개만 (설명·마크다운 금지).
스키마:
{"intent":"add|list|complete|remove|unknown","slots":{"task_text":null,"task_id":null,"task_keyword":null,"due_date":null},"needs_clarification":false,"clarification_question":null,"confidence":0.0,"risky_action":false,"rationale_ko":null}
intent가 complete 또는 remove이면 risky_action은 true. 불명확하면 needs_clarification true."""


def run_smoke() -> None:
    print(f"[smoke] 모델: ", end="")
    from todolist_chatbot import config

    print(config.OPENAI_CHAT_MODEL)
    llm = LLMInterpreter()
    messages = [
        {
            "role": "system",
            "content": "당신은 친절한 도우미입니다. 한국어로 짧게 답하세요.",
        },
        {"role": "user", "content": "안녕! 연결 테스트야. 한 문장으로만 답해줘."},
    ]
    reply = llm.chat(messages, temperature=0.3, max_tokens=256)
    print("[smoke] 응답:\n", reply)
    print("[smoke] OK")


def run_intent_sample() -> None:
    llm = LLMInterpreter()
    user = "일일 회의 추가해줘"
    raw = llm.interpret_raw(user, _INTENT_SYSTEM, json_response=True)
    print("[intent] 원문:\n", raw)
    try:
        data = json.loads(raw)
        print("[intent] JSON 파싱 OK, intent =", data.get("intent"))
    except json.JSONDecodeError as e:
        print("[intent] JSON 파싱 실패:", e)


def run_repl() -> None:
    llm = LLMInterpreter()
    system = "당신은 친절한 도우미입니다. 사용자와 자연스럽게 한국어로 대화하세요."
    history: list[dict[str, str]] = [{"role": "system", "content": system}]
    print("[repl] 종료: exit 또는 quit 입력\n")
    while True:
        try:
            line = input("나> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[repl] 종료")
            break
        if not line:
            continue
        if line.lower() in ("exit", "quit", "q"):
            print("[repl] 종료")
            break
        history.append({"role": "user", "content": line})
        reply = llm.chat(history, temperature=0.5, max_tokens=512)
        print("봇>", reply)
        history.append({"role": "assistant", "content": reply})
        # 컨텍스트 과다 방지: system 제외 최근 10턴(20메시지)만 유지
        if len(history) > 21:
            history = [history[0], *history[-20:]]


def main() -> None:
    p = argparse.ArgumentParser(description="OpenAI LLMInterpreter 스모크/대화 테스트")
    p.add_argument(
        "--repl",
        action="store_true",
        help="터미널 다회차 대화",
    )
    p.add_argument(
        "--intent-only",
        action="store_true",
        help="스모크 생략, intent JSON 샘플만",
    )
    p.add_argument(
        "--skip-intent",
        action="store_true",
        help="스모크만 (기본과 함께 쓸 때 intent 생략)",
    )
    args = p.parse_args()

    if args.repl:
        run_repl()
        return

    if args.intent_only:
        run_intent_sample()
        return

    run_smoke()
    if not args.skip_intent:
        print()
        run_intent_sample()


if __name__ == "__main__":
    main()
