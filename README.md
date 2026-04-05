# Discord 자연어 Todo 챗봇

Python · discord.py · Supabase(Postgres). 자연어 intent/slot은 **OpenAI Chat Completions**(`LLMInterpreter`, 기본 **`gpt-4o-mini`**)가 담당하고, **상태 변경은 Service → Repository**로만 수행한다.

**환경 변수:** `OPENAI_API_KEY` (필수), 선택 `OPENAI_CHAT_MODEL`(기본 `gpt-4o-mini`), `OPENAI_BASE_URL`(Azure 등 호환 시).

- **설계:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **DB DDL:** [sql/001_init.sql](sql/001_init.sql)
- **패키지:** `src/todolist_chatbot/`
- **레거시 RAG:** `legacy/rag_stack/`

`PYTHONPATH`에 프로젝트 루트와 `src`를 함께 넣는다 (`app.main` + `todolist_chatbot`).
