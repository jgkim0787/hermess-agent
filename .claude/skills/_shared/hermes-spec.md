# Hermes — 복제 프로젝트 사양 (source of truth)

> 학습자가 과정 내내 **직접 타이핑해 만들어 가는** 미니 에이전트의 단일 사양.
> 클론 단계(`clone-mentor`/`clone-building`)는 이 사양을 한 모듈씩 구현해 나간다.
> 목적: "내가 이해한 개념이 코드로 어떻게 구현되는가"를 손으로 확인하는 것. 완성도보다 이해가 우선.

## 무엇을 만드는가

**Hermes** — Python + Claude API로 만드는, 도구를 반복 호출하는 에이전트.
과정을 거치며 세 성격을 차례로 흡수한다:
- **코딩 에이전트** (M2–M4): 파일/셸 도구를 쓰는 ReAct 루프 — Claude Code의 축소판
- **자율 에이전트** (M5): 목표를 받아 스스로 계획·실행, 위험 행동은 승인
- **RAG 에이전트** (M6): 문서를 검색해 지식 기반으로 답변
- **통합** (M7): 위 셋을 한 에이전트로

> 완전 동일 복제가 목표가 아니다. **핵심 메커니즘**(agent loop, tool 왕복, 메모리, 계획, retrieval)을 담되 단순하게.

## 기술 스택 / 규약

- 언어: **Python 3.10+**
- LLM: **Anthropic Claude API** — SDK `anthropic`
- 기본 모델: `claude-sonnet-4-6` (cost-효율·고성능). 빠르고 싸게: `claude-haiku-4-5`. 모델은 `hermes/config.py` 한 곳에서 상수로.
- 외부 의존 최소화: `anthropic` 필수. M6 RAG도 가급적 순수 파이썬(코사인 유사도)으로 — 무거운 vector DB 도입 금지.
- 비밀키: `.env`의 `ANTHROPIC_API_KEY` (코드에 하드코딩 금지). `python-dotenv` 또는 환경변수.
- 스타일: 표준 라이브러리 우선, 작은 함수, 타입 힌트 권장. 학습용이므로 **읽기 쉬움 > 영리함**.

## 목표 디렉토리 구조 (과정 종료 시점)

```
clone-project/
├── .env.example          # ANTHROPIC_API_KEY=...
├── requirements.txt      # anthropic, python-dotenv
├── README.md
└── hermes/
    ├── __init__.py
    ├── config.py         # MODEL, MAX_TOKENS 등 상수
    ├── llm.py            # Claude 호출 래퍼 (M0–M1)
    ├── tools.py          # 도구 정의 + 실행기 (M2–M3, M5, M6에서 확장)
    ├── memory.py         # 대화 메모리 + 컨텍스트 관리 (M4)
    ├── rag.py            # 임베딩/검색 (M6)
    ├── agent.py          # agent loop = Hermes 본체 (M3에서 등장, 이후 확장)
    └── __main__.py       # CLI 진입점 (python -m hermes)
```

학습자는 빈 폴더에서 시작해 모듈마다 파일을 한두 개씩 추가/확장한다.

## 모듈별 클론 증분 (incremental build)

각 단계는 **이전 단계 위에 더한다**. 단계마다 "돌려서 확인할 수 있는 상태"를 만든다.

### M0 — 두뇌만
- `config.py`: `MODEL = "claude-sonnet-4-6"`, `MAX_TOKENS = 1024`.
- `llm.py`: `ask(prompt: str) -> str` — 단발 `messages.create` 호출, 첫 text 블록 반환.
- `__main__.py`: 인자로 받은 질문을 `ask`로 보내 출력.
- 확인: `python -m hermes "안녕"` → 응답. 두 번 호출해도 직전 대화를 기억 못 함을 확인(→ 메모리 필요성 동기).

### M1 — 멀티턴 + 스트리밍
- `llm.py`: `chat(messages: list) -> str`(history 받기), `stream_chat(messages)`(토큰 스트리밍). `SYSTEM`(persona) 상수.
- `__main__.py`: REPL — 입력을 받아 history에 누적, 스트리밍 출력. `exit`로 종료.
- 확인: 이름을 말한 뒤 "내 이름?" → 기억(history 덕분).

### M2 — 첫 도구 (1-step)
- `tools.py`: 도구 정의 리스트 `TOOLS`(JSON Schema) + `run_tool(name, input) -> str` 디스패처. 첫 도구 `read_file(path)`.
- `llm.py`/스크립트: `tools=`를 넘겨 호출. 응답의 `tool_use` 블록을 꺼내 `run_tool` 실행, `tool_result`로 한 번 회신해 최종 답 받기(아직 while 루프 아님).
- 확인: "README.md 첫 줄 알려줘" → read_file 호출 → 답변.

### M3 — Agent Loop (코딩 에이전트 완성)
- `agent.py`: `class Hermes` — `run(user_msg)`가 **while 루프**로 `stop_reason`이 `end_turn`이 될 때까지 도구를 반복 실행. `max_steps` 가드.
- `tools.py`: `write_file(path, content)`, `run_bash(cmd)` 추가. (run_bash는 학습용 — 위험성 경고 주석 필수, M5에서 승인 게이트로 보강.)
- 확인: "이 폴더 .py 파일 목록을 files.txt로 저장해줘" 류 멀티스텝 수행.

### M4 — Memory & Context
- `memory.py`: `class Memory` — 메시지 누적, `token_estimate`, 임계 초과 시 오래된 메시지를 **요약 1개로 압축**(별도 LLM 호출).
- `agent.py`: history를 `Memory`로 교체.
- 확인: 긴 대화 후에도 컨텍스트 한도 안에서 동작(요약 발생 로그 확인).

### M5 — Planning & Autonomy (자율 에이전트)
- `tools.py`: `update_plan(steps)` 도구(현재 계획을 상태로 보관/표시). 위험 도구(`write_file`/`run_bash`)에 **승인 게이트**: 실행 전 사용자에게 `confirm`.
- `agent.py`: 목표 한 줄을 받으면 먼저 계획을 세우도록 system/prompt 유도, 위험 도구는 승인 후 실행.
- 확인: "프로젝트 정리해줘" → 계획 출력 → 단계 실행, 파일 쓰기 전 승인 요청.

### M6 — RAG & Knowledge (RAG 에이전트)
- `rag.py`: 문서 폴더를 청크로 나눠 **임베딩**(간단히: Claude로 요약 키워드 or 순수 파이썬 TF-IDF/코사인 — 외부 vector DB 금지), `search(query, k) -> [chunks]`.
- `tools.py`: `search_docs(query)` 도구 추가(내부적으로 `rag.search`).
- 확인: 로컬 문서에만 있는 사실을 질문 → search_docs로 찾아 답변.

### M7 — 통합 + 관찰 (Capstone)
- 모든 도구를 한 Hermes에 통합. 실행 trace를 `logs/`에 남기는 간단 로깅.
- 작은 eval: 정해둔 질문 1~2개에 대해 기대 동작(특정 도구 호출/특정 출력 포함)을 체크하는 스크립트.
- 확인: "이 코드베이스 요약 + 관련 문서 검색해서 정리 문서 작성" 같은 복합 데모.

## 가르칠 때의 강조점 (clone-mentor 용)

- 매 단계 **개념 ↔ 코드 매핑**을 명시: "M3에서 배운 ReAct 루프 = `agent.py`의 이 while".
- 코드는 **조각으로 제시하고 누적**한다. 한 번에 전체 파일을 덤프하지 말 것 — 학습자가 타이핑하며 따라올 수 있게 작은 블록 + "지금 무엇을/왜".
- 매 단계 끝에 **"돌려보기"**(실행 명령 + 기대 출력)와 **"막히면"**(흔한 에러: 키 미설정, 모델명 오타, tool_result 누락) 섹션.
- 보안/비용 주의: API 키 노출 금지, `run_bash` 위험성, 토큰 비용 감각.
