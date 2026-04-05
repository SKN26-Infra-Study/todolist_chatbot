# Discord 자연어 Todo 챗봇 — 아키텍처 설계

## 1. 프로젝트 목표 요약

- Discord에서 **명령어 강제 없이** 자연어로 Todo를 관리한다.
- **LLM**은 `intent` 분류와 `slot` 채우기만 수행하며, **DB/상태 변경은 하지 않는다**.
- **실제 CRUD**는 **Service → Repository** 경로로만 수행한다.
- **discord.py**, **Cog** 기반, **Supabase(Postgres)**, 관계형 2테이블(`rooms`, `todos`), 벡터 DB 없음.

---

## 2. 계층별 책임·입출력·의존성

### 2.1 BotCore

| 항목 | 내용 |
|------|------|
| **책임** | Discord 봇 프로세스 수명 주기: 토큰 로드, `discord.Client`/`commands.Bot` 생성, Cog 로드, 이벤트 루프 시작/종료, 전역 예외 로깅 훅(선택). |
| **입력** | 설정(토큰, intents), 등록할 Cog 목록. |
| **출력** | 실행 중인 봇 인스턴스(또는 graceful shutdown). |
| **의존** | `TodoCog` 등 Cog 모듈만 알면 됨. DB/LLM/대화 로직에 직접 의존하지 않는 것이 이상적. |
| **DB 접근** | 없음. |
| **LLM 접근** | 없음. |
| **Discord** | 봇 연결·Cog 등록의 최상위 진입점. |

---

### 2.2 TodoCog

| 항목 | 내용 |
|------|------|
| **책임** | Discord 이벤트(예: `on_message`)에서 **메시지 수신** → 라우터/대화 매니저에 위임 → **포맷된 문자열**을 채널에 회신. 권한/봇 자신 메시지 무시 등 Discord 규칙 처리. |
| **입력** | `discord.Message`, (선택) 세션/상태는 `DialogueManager`가 보관. |
| **출력** | `channel.send(...)` 등 Discord API 호출. |
| **의존** | `NaturalLanguageRouter`(또는 `MessageListener` 래퍼), `ResponseFormatter`(또는 포맷 유틸). **Service/Repository/LLM에 직접 의존하지 않는 것**을 권장(얇은 Cog). |
| **DB 접근** | 없음(간접적으로 Service를 타더라도 Cog 안에서 raw SQL 금지). |
| **LLM 접근** | 없음(Interpreter는 하위 계층). |
| **Discord** | **이벤트 수신의 1차 계층.** |

---

### 2.3 NaturalLanguageRouter (MessageListener)

| 항목 | 내용 |
|------|------|
| **책임** | 메시지 전처리(길이 제한, 빈 메시지, 멘션 제거 등), **대화 컨텍스트 키** 결정(예: `guild_id + channel_id + user_id`), `DialogueManager`에 **한 턴 처리** 요청, 반환된 **사용자용 텍스트**를 Cog에 넘김. |
| **입력** | 정제된 사용자 텍스트, Discord 식별자(room/user/guild). |
| **출력** | 최종 사용자에게 보낼 문자열(또는 구조화된 `BotReply` + Formatter 위임). |
| **의존** | `DialogueManager`에 의존. LLM/DB 직접 호출 없음. |
| **DB 접근** | 없음. |
| **LLM 접근** | 없음. |
| **Discord** | Cog 다음 단계; Discord 이벤트는 Cog가 받고 Router는 “애플리케이션 유스케이스 진입” 역할. |

> **이름 정리:** `MessageListener`는 “이벤트만 받는다”에 가깝고, `NaturalLanguageRouter`는 “어느 유스케이스로 보낼지 라우팅”에 가깝다. 구현 시 **하나의 클래스**로 묶어도 되고, Listener가 Router를 호출해도 된다.

---

### 2.4 LLMInterpreter

| 항목 | 내용 |
|------|------|
| **책임** | 사용자 발화 + (선택) 최근 대화/슬롯 힌트를 넣고, **JSON 한 덩어리**로 `intent` + `slots` + `needs_clarification` 등을 파싱. **도구 호출·SQL 생성·파일 쓰기 금지** 정책을 시스템 프롬프트로 고정. |
| **입력** | 자연어 문자열, 선택적 컨텍스트(직전 intent, 후보 task 목록 요약 등). |
| **출력** | 파싱된 구조체(예: `InterpretationResult`: intent, slots, confidence, clarification_question). |
| **의존** | LLM 클라이언트(OpenAI 등)만. Repository/Service **비의존**. |
| **DB 접근** | 없음. |
| **LLM 접근** | **유일한(또는 주된) LLM 호출 지점.** |
| **Discord** | 없음. |

---

### 2.5 DialogueManager

| 항목 | 내용 |
|------|------|
| **책임** | (1) `LLMInterpreter` 결과와 **세션 상태**(예: pending clarification, 마지막 후보 목록)를 합쳐 **실행 가능 여부** 판단. (2) 충분하면 `RoomService`/`TodoService` 호출. (3) 부족/모호하면 clarification만 반환. (4) `remove`/`complete` 등 **고위험** intent는 매칭이 불명확하면 **실행하지 않고** 확인 질문. (5) `unknown`은 안내 메시지. |
| **입력** | 사용자 텍스트, room/user 식별자, (내부) 세션 상태. |
| **출력** | 사용자 메시지 문자열 또는 `TodoService` 실행 결과를 Formatter에 넘길 DTO. |
| **의존** | `LLMInterpreter`, `RoomService`, `TodoService`, (선택) `ResponseFormatter` 또는 포맷 헬퍼. |
| **DB 접근** | 없음(항상 Service 경유). |
| **LLM 접근** | Interpreter를 통해서만. |
| **Discord** | 없음. |

---

### 2.6 TodoService

| 항목 | 내용 |
|------|------|
| **책임** | Todo 도메인 유스케이스: 추가/목록/완료/삭제의 **비즈니스 규칙**(예: 동일 room 내 제목 중복 정책, 완료 토글, 키워드 검색 후 삭제 후보 확정 전략은 DialogueManager와 협력). **트랜잭션 경계**는 여기 또는 Repository에서 명확히. |
| **입력** | `room_id`(내부 PK), `discord_user_id`, 슬롯 값(task_text, task_id, keyword, due_date 등). |
| **출력** | 도메인 결과(DTO): 생성된 todo, 목록, 영향 row 수 등. |
| **의존** | `TodoRepository`, (필요 시) `RoomService`로 room 보장. |
| **DB 접근** | **Repository를 통해서만.** |
| **LLM 접근** | 없음. |
| **Discord** | 없음. |

---

### 2.7 RoomService

| 항목 | 내용 |
|------|------|
| **책임** | Discord room(channel/thread) 식별자로 `rooms` row **조회 또는 생성(get-or-create)**, 내부 `room_id`(PK) 반환. 이름 변경 시 `room_name` 갱신(선택). |
| **입력** | `discord_room_id`, `guild_id`, 표시용 `room_name`. |
| **출력** | `Room` 엔티티 또는 `id`. |
| **의존** | `RoomRepository`만. |
| **DB 접근** | **Repository를 통해서만.** |
| **LLM 접근** | 없음. |
| **Discord** | 없음(식별자는 Cog/Router가 넘김). |

---

### 2.8 Repository layer

| 항목 | 내용 |
|------|------|
| **책임** | Supabase/Postgres에 대한 **SQL 또는 공식 클라이언트** 호출. CRUD 쿼리 캡슐화. |
| **입력** | Service가 넘긴 파라미터. |
| **출력** | row dict / dataclass / None. |
| **의존** | DB 드라이버(Supabase Python client 등), 연결 설정. |
| **DB 접근** | **이 계층만 직접 DB에 닿는다** (앱 기준). |
| **LLM 접근** | 없음. |
| **Discord** | 없음. |

---

### 2.9 ResponseFormatter

| 항목 | 내용 |
|------|------|
| **책임** | Service 결과·clarification·에러를 **Discord용 한국어 문자열**로 통일된 톤으로 변환(목록 번호 매기기, 완료 체크 표시 등). |
| **입력** | DTO 또는 `DialogueTurnResult`. |
| **출력** | 문자열(또는 embed용 dict, 프로젝트 정책에 맞게). |
| **의존** | 순수 함수 수준 권장(다른 계층에 거의 의존하지 않음). |
| **DB 접근** | 없음. |
| **LLM 접근** | 없음(문구는 템플릿 기반 권장). |
| **Discord** | 없음(포맷만; 전송은 Cog). |

---

## 3. “누가 무엇에 접근하는가” 한눈에

| 접근 대상 | 계층 |
|-----------|------|
| Discord 이벤트 | **TodoCog** (최초), Router는 앱 진입 |
| LLM API | **LLMInterpreter** |
| Postgres(Supabase) | **Repository** (Service는 Repository만 호출) |
| 상태 변경(CRUD) | **TodoService**, **RoomService** |

---

## 4. 대화 흐름 (텍스트 시퀀스)

### 4.1 "일일 회의 추가해줘"

1. **TodoCog** `on_message`: 봇 자신/빈 메시지 필터 → **Router**에 위임.  
2. **Router**: room/user/guild 식별자 추출 → **DialogueManager.handle_turn**.  
3. **DialogueManager**: **RoomService.get_or_create** → 내부 `room_id` 확보.  
4. **LLMInterpreter**: JSON → `intent: add`, `slots: { task_text: "일일 회의" }`, `needs_clarification: false`.  
5. **DialogueManager**: 슬롯 충분 → **TodoService.create**(`room_id`, `discord_user_id`, task_text).  
6. **TodoService** → **TodoRepository.insert**.  
7. **ResponseFormatter**: "‘일일 회의’ 할 일을 추가했어요."  
8. **TodoCog** `channel.send`.

---

### 4.2 "내 할 일 보여줘"

1. Cog → Router → DialogueManager.  
2. RoomService로 `room_id` 확보.  
3. LLMInterpreter: `intent: list`, (선택) `slots`에 user 스코프 힌트.  
4. DialogueManager: **TodoService.list_by_room**(및 정책상 "내"면 `discord_user_id` 필터).  
5. Formatter로 번호 목록 문자열 생성.  
6. Cog 전송.

---

### 4.3 "그거 완료해줘" (지시어·컨텍스트 의존)

1. Cog → Router → DialogueManager.  
2. RoomService로 `room_id` 확보.  
3. **DialogueManager**가 세션에 **직전에 생성/언급된 todo 후보**(예: 마지막 추가 id, 또는 최근 N개 미완료 목록 요약)를 Interpreter 컨텍스트로 전달.  
4. LLMInterpreter: `intent: complete`, `slots: { task_id: <단일 후보> }` 또는 `needs_clarification: true` + 후보가 여러 개면 질문 생성.  
5. **고위험 규칙**: `task_id`가 **단 하나로 확정**되지 않으면 **TodoService 호출 안 함** → clarification.  
6. 확정 시 **TodoService.mark_done**.  
7. Formatter → 전송.

---

### 4.4 "회의 지워줘"처럼 모호한 경우

1. Cog → Router → DialogueManager + room 확보.  
2. LLMInterpreter: `intent: remove`, `slots: { task_keyword: "회의" }`.  
3. **TodoService.search**로 해당 room(및 필요 시 user)에서 매칭 후보 **복수** 가능.  
4. DialogueManager: 후보 0개 → "찾을 수 없어요"; 2개 이상 → **삭제 대상 나열 + 번호/제목으로 확인 요청**; 1개이지만 LLM confidence 낮음 → 정책에 따라 확인 한 번 더(고위험).  
5. 사용자가 다음 턴에 명확히 하면 그때 **TodoService.delete**.  
6. Formatter → 전송.

---

## 5. Cog 기반 폴더 구조 제안

```text
todolist_chatbot/
├── app/
│   └── main.py                 # 진입점: BotCore 실행
├── docs/
│   └── ARCHITECTURE.md
├── sql/
│   └── 001_init.sql
├── src/
│   └── todolist_chatbot/
│       ├── __init__.py
│       ├── config.py
│       ├── bot/
│       │   ├── __init__.py
│       │   └── core.py         # BotCore
│       ├── cogs/
│       │   ├── __init__.py
│       │   └── todo_cog.py
│       ├── nlu/
│       │   ├── __init__.py
│       │   └── router.py       # NaturalLanguageRouter
│       ├── llm/
│       │   ├── __init__.py
│       │   └── interpreter.py  # LLMInterpreter
│       ├── dialogue/
│       │   ├── __init__.py
│       │   └── manager.py      # DialogueManager
│       ├── services/
│       │   ├── __init__.py
│       │   ├── room_service.py
│       │   └── todo_service.py
│       ├── repositories/
│       │   ├── __init__.py
│       │   ├── supabase.py     # 클라이언트 팩토리(선택)
│       │   ├── room_repository.py
│       │   └── todo_repository.py
│       └── formatters/
│           ├── __init__.py
│           └── response_formatter.py
├── legacy/
│   ├── README.md
│   └── rag_stack/              # 이전 RAG 실험 코드
├── data/                       # 샘플 데이터 등(선택)
├── notebooks/                  # 실험용(선택)
├── requirements.txt
└── README.md
```

---

## 6. Room 생성·조회 전략 (get-or-create)

1. 메시지 수신 시 Discord에서 **채널(또는 스레드) ID**를 `discord_room_id`로 사용한다. (스레드를 별도 room으로 볼지 정책 결정 — 권장: **스레드도 별도 room**이면 `discord_room_id = thread.id`, 아니면 부모 채널 id로 통일.)  
2. **RoomRepository.find_by_discord_room_id**(및 필요 시 `guild_id` 복합 유니크).  
3. 없으면 **insert**: `guild_id`, `room_name`(채널명 스냅샷), `discord_room_id`.  
4. 반환된 PK `rooms.id`를 모든 Todo 조회/생성의 `room_id`로 사용한다.  
5. **Race condition**: 동시에 첫 메시지가 오면 유니크 제약 + `ON CONFLICT` upsert 또는 트랜잭션 내 재조회 패턴을 Repository에 캡슐화한다.

---

## 7. Supabase SQL DDL 초안

`sql/001_init.sql`과 동일 내용을 유지한다. (파일 참조)

---

## 8. LLM 프롬프트 설계 초안 (JSON 출력)

**시스템 역할 요지**

- 너는 Discord Todo 봇의 **의도 분석기**다.  
- **데이터베이스를 수정하지 않는다.** 출력은 **JSON 한 개**만.  
- intent는 반드시 다음 중 하나: `add`, `list`, `complete`, `remove`, `unknown`.  
- 슬롯: `task_text`, `task_id`, `task_keyword`, `due_date`(ISO 8601 날짜 문자열 또는 null), 부족하면 null.  
- `needs_clarification`: true면 `clarification_question`에 한국어 질문 한 문장.  
- `risky_action`: intent가 `remove` 또는 `complete`이면 true.  
- 후보 task 목록이 컨텍스트로 주어지면, `task_id`는 그 목록의 id만 사용한다.

**출력 스키마 예시**

```json
{
  "intent": "add",
  "slots": {
    "task_text": "string|null",
    "task_id": "integer|null",
    "task_keyword": "string|null",
    "due_date": "string|null"
  },
  "needs_clarification": false,
  "clarification_question": "string|null",
  "confidence": 0.0,
  "risky_action": false,
  "rationale_ko": "한 줄 요약(디버그용, 선택)"
}
```

**사용자 메시지 구성 예시**

```text
[현재 사용자 발화]
{user_message}

[컨텍스트]
- guild_id, channel_id, user_id (참고만, DB 조회 금지)
- 최근 대화 요약 또는 마지막에 추가된 todo_id, 미완료 목록 상위 N개 (있다면)
```

---

## 9. 구현 순서 권장

1. DDL 적용 + Repository 스텁 + Supabase 연결 확인  
2. RoomService get-or-create + TodoService CRUD 최소 구현  
3. LLMInterpreter + JSON 검증(Pydantic 등)  
4. DialogueManager 규칙(고위험 clarification)  
5. TodoCog + Router + Formatter + BotCore 연결  
6. 세션 저장(메모리 → 이후 Redis/DB)은 필요 시 확장  

---

## 10. 레거시 코드

기존 RAG/벡터 관련 코드는 `legacy/rag_stack/`으로 이동했다. 본 Todo 봇 요구사항(벡터 DB 미사용)과 분리한다.
