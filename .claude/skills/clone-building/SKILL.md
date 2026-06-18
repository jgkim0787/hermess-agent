---
name: clone-building
description: >-
  한 모듈의 "Hermes 만들기"(복제 프로젝트) 섹션을 집필하는 절차. 미니 에이전트 Hermes를 모듈마다 한 겹씩
  키우는 증분 빌드를 개념↔코드 매핑과 함께 안내한다. "복제/클론/Hermes 만들기" 및 모듈 빌드의 클론 단계에서 사용. clone-mentor 에이전트가 사용.
---

# 클론 빌드 (clone-building)

## 먼저 읽을 것
- `_workspace/{slug}_spec.md`, `_shared/hermes-spec.md` (구조·증분 진실), `_shared/claude-api-cheatsheet.md` (API), `_shared/content-conventions.md`.

## 원칙
- hermes-spec의 해당 모듈 증분을 **이전 단계 위에** 구현한다. 파일 구조/이름은 hermes-spec을 따른다.
- **코드는 조각으로 누적**: 작은 블록 + "지금 무엇을/왜" + "어느 파일 어디에". 전체 파일 덤프 금지.
- 매 단계 **개념↔코드 매핑** 한 줄(예: "M3 ReAct 루프 = `agent.py`의 while").
- 클론은 **수동 agent loop를 직접 구현**(자동 `tool_runner`는 '쉬운 길'로 소개만).
- 단순·가독성 우선, 외부 의존 최소(M6 RAG는 순수 파이썬). 보안/비용 주의(키 하드코딩·`run_bash` 위험·토큰).

## 한 단계의 구성
1. **이번에 추가할 것**(개념↔코드 한 줄) → 2. **코드 블록**(작게, 넣을 위치 명시) → 3. **돌려보기**(명령 + 기대 출력) → 4. **막히면**(흔한 에러).

## 모듈별 증분 요지(hermes-spec 따름)
- M0: `config.py`,`llm.py(ask)`,`__main__.py` — 두뇌만.
- M1: `chat/stream_chat`, REPL, `SYSTEM`.
- M2: `tools.py(TOOLS, run_tool, read_file)` + 1-step.
- M3: `agent.py(Hermes.run, while, max_steps)` + `write_file/run_bash` → 코딩 에이전트.
- M4: `memory.py(Memory, 토큰 추정, 요약 압축)`.
- M5: `update_plan` 도구 + 위험 도구 승인 게이트 → 자율.
- M6: `rag.py(임베딩/검색)` + `search_docs` 도구 → RAG.
- M7: 통합 + 실행 trace 로깅 + 간단 eval.

## HTML 형식 (조각)
```html
<section class="module-section" id="clone">
  <h2>Hermes 만들기</h2>
  <p>이번 단계: <em>…개념↔코드…</em></p>
  <h3>1) hermes/tools.py 에 read_file 추가</h3>
  <pre><code class="language-python">…</code></pre>
  <pre><code class="language-bash">python -m hermes "README.md 첫 줄 알려줘"</code></pre>
  <pre class="output">…</pre>
  <div class="callout warn"><strong>막히면:</strong> tool_result 누락 시 400 …</div>
</section>
```
→ `_workspace/{slug}_clone.html` (선택: 참조 해답 `clone-project/_solution/{slug}/`)

## 출력 체크
- [ ] 이전 단계 위 누적  [ ] 개념↔코드 매핑  [ ] 돌려보기+기대출력  [ ] 막히면  [ ] 수동 루프(자동러너 아님)  [ ] 키/위험 주의
