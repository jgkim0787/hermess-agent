# 커리큘럼 — AI Agent 입문 (Hermes 과정)

> 이 파일은 하네스 전체의 **커리큘럼 단일 진실(source of truth)**이다.
> `docs/data/curriculum.json`은 이 파일을 기계가 읽을 수 있게 옮긴 것이며, 둘은 항상 동기화한다.
> 모듈 추가/수정 시 이 파일 → `curriculum.json` → 사이트 순으로 반영한다.

## 대상과 톤

- **대상**: 전문 SW 개발자. 일반 SW/도구 개념(HTTP, JSON, 프로세스, 재귀, 상태머신 등)은 설명 없이 사용한다.
- **단, AI Agent 영역은 입문자**로 간주한다. `token`, `prompt`, `tool calling`, `ReAct`, `embedding`, `context window` 같은 용어는 **처음 등장할 때 반드시 정의**한다.
- 언어: 한글. 전문 용어는 영어 원어 그대로(번역하지 않음). 코드/주석은 한글 주석 허용.

## 과정 전체 구조

각 모듈은 항상 3개 학습 요소를 가진다:
1. **개념 (concept)** — 주요 개념 설명. 아는 SW 개념에 빗댄 analogy 적극 사용.
2. **실습 (practice)** — 직접 타이핑해 돌려보는 코드. "사용해보기".
3. **클론 단계 (hermes step)** — `Hermes` 에이전트를 한 겹 키우는 작업. "만들어보기".

Hermes는 과정을 거치며 **코딩 에이전트 → 자율 에이전트 → RAG 에이전트**의 세 성격을 차례로 흡수해 마지막에 통합된다.

## 모듈 목록 (M0–M7, 집중 입문안)

| # | slug | 제목 | 한 줄 | 다루는 flavor |
|---|------|------|-------|--------------|
| 0 | `00-what-is-an-agent` | AI Agent란 무엇인가 | LLM vs Agent, 구성요소, 첫 API 호출 | 공통 |
| 1 | `01-llm-basics` | LLM 다루기 | token·message·system·stop_reason·streaming·stateless | 공통 |
| 2 | `02-tool-use` | Tool Use (도구 사용) | tool_use/tool_result, input_schema, 1-step | 코딩 |
| 3 | `03-agent-loop` | The Agent Loop | ReAct, while 루프, 종료 조건, 멀티스텝 | 코딩 |
| 4 | `04-memory-context` | Memory & Context | 대화 메모리, context window, 압축, persona | 코딩 |
| 5 | `05-planning-autonomy` | Planning & Autonomy | 목표 분해, plan 도구, 승인 게이트, 가드레일 | 자율 |
| 6 | `06-rag-knowledge` | RAG & Knowledge | embedding, vector search, retrieval 도구 | RAG |
| 7 | `07-hermes-capstone` | Hermes 완성 | 세 flavor 통합, 데모, eval·관찰 맛보기 | 통합 |

## 모듈별 상세 목표

### M0 — AI Agent란 무엇인가
- 개념: LLM은 "텍스트 in → 텍스트 out"의 **stateless 함수**. Agent = LLM + **loop** + **tools** + **goal**. 자율성 = decide→act→observe 반복. 왜 지금(tool calling·long context·추론 향상). Claude Code 자체가 에이전트라는 점.
- 실습: `anthropic` 설치, `ANTHROPIC_API_KEY` 설정, 첫 `messages.create` 호출. 같은 질문을 두 번 보내 "기억 못 함(stateless)"을 체험.
- Hermes 단계: 프로젝트 스캐폴드 + `hermes/llm.py`(Claude 호출 래퍼, "두뇌"만). 아직 루프·도구 없음.

### M1 — LLM 다루기
- 개념: `token`/토큰 비용, `messages` 배열 구조(user/assistant), `system` prompt, `max_tokens`, `stop_reason`, **API는 stateless라 매 호출에 전체 history를 보낸다**, `streaming`.
- 실습: 멀티턴 대화 루프(history 직접 관리), system prompt로 말투 바꾸기, 스트리밍 출력.
- Hermes 단계: `llm.py`를 멀티턴 + 스트리밍 지원으로 확장. 간단한 REPL.

### M2 — Tool Use
- 개념: LLM은 직접 행동 못 함 → **도구를 "호출 요청"**하고 우리가 실행해 결과를 돌려준다. `tools` 정의(`input_schema`=JSON Schema), 응답의 `tool_use` 블록, 우리가 보내는 `tool_result` 블록, `tool_use_id` 매칭.
- 실습: `get_weather`(가짜) 도구 1개 정의 → 1회 호출 → 결과 회신 → 최종 답변. tool_use/tool_result 왕복을 눈으로 확인.
- Hermes 단계: 첫 진짜 도구 `read_file` 정의, 1-step 실행(루프는 아직).

### M3 — The Agent Loop
- 개념: **ReAct**(Reasoning+Acting) = 사고→행동→관찰 반복. `while` 루프, `stop_reason == "tool_use"`면 도구 실행 후 계속, `end_turn`이면 종료. 멀티스텝(여러 도구 연쇄), 무한루프 방지(max steps).
- 실습: 계산기 도구로 멀티스텝 질문("(12+8)*3 을 단계별로") 해결하는 미니 루프.
- Hermes 단계: **agent loop 구현**. 도구 `read_file`/`write_file`/`run_bash` 추가. "이 폴더 파일 읽고 README 써줘" 류 멀티스텝 태스크 수행 → 코딩 에이전트 완성.

### M4 — Memory & Context
- 개념: 대화 메모리(history 누적), `context window`(한도) 개념과 비용, 길어지면 **요약/압축(compaction)**·오래된 tool 결과 정리, `system` prompt로 persona·항구 규칙.
- 실습: history가 길어질 때 토큰을 세고(간단 추정), 오래된 메시지를 요약으로 대체하는 미니 compaction.
- Hermes 단계: 대화 메모리 관리 모듈 + 컨텍스트 길이 가드(임계 초과 시 요약).

### M5 — Planning & Autonomy
- 개념: 목표를 **하위 단계로 분해**, todo/plan을 명시적으로 유지, 자율 실행. **가드레일**: 위험·되돌리기 어려운 도구(삭제, 외부 전송)는 **승인 게이트**. 자율성과 안전의 균형.
- 실습: "plan 먼저 세우고 실행" 패턴, 위험 도구 호출 전 사용자 confirm 받기.
- Hermes 단계: `update_plan` 도구 + 위험 도구 승인 게이트. 목표 한 줄 받아 스스로 계획·실행 → 자율 에이전트 요소.

### M6 — RAG & Knowledge
- 개념: 모델이 모르는 지식을 **검색해 넣어주기**. `embedding`(텍스트→벡터), 유사도 검색(vector search), retrieval을 **도구로** 노출. RAG = Retrieval-Augmented Generation.
- 실습: 문서 몇 개를 임베딩/유사도로 검색하는 작은 인덱스(외부 의존 최소, 가능하면 순수 파이썬 코사인 유사도) + "검색해서 답하기".
- Hermes 단계: `search_docs` 도구 추가 → 지식 기반 질문에 답하는 RAG 에이전트 요소.

### M7 — Hermes 완성 (Capstone)
- 개념: 세 flavor 통합 회고, **eval**(에이전트 품질을 어떻게 측정?), **관찰/로깅**(무슨 일이 있었나), 한계와 다음 단계(멀티에이전트, MCP, managed agents 등 포인터).
- 실습: 통합 Hermes로 실제 멀티스텝 데모(코드 읽고 + 계획 + 문서 검색 + 결과 작성), 실행 로그 살펴보기.
- Hermes 단계: 도구 통합 + 실행 trace 로깅 + 간단한 eval 체크 1개.

## 진행 규칙

- 사용자는 보통 한 번에 한 모듈을 학습한다("N강 배우자", "다음 강의").
- 모듈 생성 시 `curriculum.json`의 해당 모듈 `status`를 `planned → in_progress → done`으로 갱신한다.
- 사용자가 모듈 도중/이후 던진 질문은 모두 `docs/data/qa-log.jsonl`에 기록한다(태그: 모듈 slug).
- 복습은 누적 질문 + 완료 모듈 요지로 생성한다(스킬 `review-generation`).

## 확장 메모

- 사용자가 "포괄 과정"으로 키우길 원하면 M8+로 멀티에이전트, evaluation 심화, guardrails/안전, MCP, managed agents를 추가한다. 추가 시 본 파일과 `curriculum.json`을 함께 갱신하고 CLAUDE.md 변경 이력에 기록한다.
