# Discord 자연어 Todo 챗봇

Python · discord.py · Supabase(Postgres). 자연어 intent/slot은 LLM이 담당하고, **상태 변경은 Service → Repository**로만 수행한다.

- **설계 전문:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **DB DDL 초안:** [sql/001_init.sql](sql/001_init.sql)
- **앱 패키지:** `src/todolist_chatbot/`
- **이전 RAG 실험 코드:** `legacy/rag_stack/` (벡터 스택, 본 봇과 분리)

로컬에서 패키지 import를 쓰려면 `src`를 `PYTHONPATH`에 추가한다.
