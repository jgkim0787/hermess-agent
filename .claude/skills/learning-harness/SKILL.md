---
name: learning-harness
description: >-
  AI Agent 입문(Hermes) 학습 과정을 운영하는 오케스트레이터. 다음 요청에 반드시 사용한다 —
  "오늘 공부/학습하자", "N강/1강/다음 강의 배우자", "모듈 만들어/열어", "개념 설명/실습/복제(클론) 자료",
  "Hermes 만들기", 학습 중 떠오른 질문 답변·기록, "복습/리마인드 자료", "사이트 갱신/배포/GitHub Pages",
  "커리큘럼 보여줘/바꿔/확장", 그리고 "다시/재실행/이어서/이전 결과 기반으로 보완" 같은 후속 요청.
  이 과정의 콘텐츠 생성·질문 기록·복습·사이트 빌드를 에이전트 팀으로 조율한다.
---

# Learning Harness — AI Agent 입문(Hermes) 과정 오케스트레이터

이 스킬은 "전문 개발자를 위한 AI Agent 입문(Hermes 과정)"을 운영한다. 개념·실습·복제 프로젝트 자료(HTML, GitHub Pages)를 만들고, 학습 중 질문에 답하고 기록하며, 복습 자료를 생성한다. **실행 모드 = 하이브리드**(모듈 빌드는 에이전트 팀, 단발 작업은 단일 서브 에이전트).

**모든 Agent/팀 호출에는 `model: "opus"`를 명시한다.** 날짜가 필요한 작업(qa-log, review 파일명)에는 대화 컨텍스트의 현재 날짜를 에이전트에 전달한다.

## 공유 진실 파일 (항상 우선)
- 커리큘럼: `.claude/skills/_shared/curriculum.md` ↔ `docs/data/curriculum.json`
- 클론 사양: `.claude/skills/_shared/hermes-spec.md`
- 작성 규약: `.claude/skills/_shared/content-conventions.md`
- API 정확성: `.claude/skills/_shared/claude-api-cheatsheet.md`

## Phase 0 — 컨텍스트 확인 (항상 먼저)
1. `docs/data/curriculum.json`을 읽어 모듈 상태(planned/in_progress/done)를 파악한다. 없으면 `_shared/curriculum.md`로부터 site-builder가 생성하게 한다.
2. `_workspace/` 존재 여부로 실행 모드를 판별한다:
   - 미존재 + 신규 자료 요청 → **초기 실행**
   - 존재 + 부분 수정 요청("이 부분만 고쳐") → **부분 재실행**(해당 에이전트만 재호출)
   - 존재 + 새 모듈/입력 → **새 실행**
3. 사용자 의도를 아래 라우팅표로 분류한다.

## 의도 라우팅
| 사용자 의도(예) | 실행 모드 | 처리 |
|---|---|---|
| "N강 배우자 / 다음 강의 / 모듈 만들어/열어" | **에이전트 팀** | 모듈 빌드 파이프라인(아래) |
| 학습 중 질문("왜 stateless야?", "이 코드 의미는?") | 단일 서브 | `learning-tutor`(qa-recording): 답변 + qa-log 기록 → site-builder가 렌더 |
| "복습 / 리마인드 / 지금까지 정리" | 단일 서브 | `learning-tutor`(review-generation): review 페이지 생성 |
| "사이트 갱신 / 미리보기 / 배포 / GitHub Pages" | 단일 서브 | `site-builder` + 배포 가이드(`references/deploy-github-pages.md`) |
| "커리큘럼 보여줘/바꿔/확장" | 단일 서브 | `curriculum-architect`(curriculum-design) → 변경 시 CLAUDE.md 이력 |
| 단순 사실 질문(자료 생성 불필요) | (직접) | 오케스트레이터가 직접 답하고, 학습 관련이면 tutor로 기록 권유 |

## 모듈 빌드 파이프라인 (에이전트 팀)
대상 모듈(slug 또는 "다음" = curriculum.json에서 planned 최소 번호)을 정한 뒤:

1. **팀 구성**: `TeamCreate`로 `curriculum-architect`, `concept-lecturer`, `practice-designer`, `clone-mentor`, `site-builder`를 멤버로(모두 `model:"opus"`).
2. **스펙(파이프라인 시작)**: architect가 모듈 스펙을 `_workspace/{slug}_spec.md`에 작성, running example·정의할 용어를 팀에 공유, `curriculum.json` 상태 `in_progress`.
3. **콘텐츠(팬아웃/병렬)**: concept-lecturer·practice-designer·clone-mentor가 스펙을 받아 각각 `_workspace/{slug}_{concept,practice,clone}.html`를 작성. 세 에이전트는 **running example·용어·표기**를 SendMessage로 맞춘다(일관성이 품질).
4. **조립(팬인)**: site-builder가 조각 + 모듈 메타를 템플릿에 끼워 `docs/modules/{slug}.html` 생성, `index.html`·`curriculum.json`(상태 `done`) 갱신, 깨진 링크 점검.
5. **보고**: 페이지 경로 + 로컬 미리보기(`python -m http.server -d docs 8000` → `http://localhost:8000/modules/{slug}.html`)를 사용자에게 안내.

> 데이터 전달: 태스크 기반(`TaskCreate`로 의존성) + 파일 기반(`_workspace/` 중간 산출물, `docs/`가 최종) + 메시지 기반(일관성 조율). 중간 파일은 보존(감사/재실행).

## 데이터 전달 프로토콜
- 중간 산출물: `_workspace/{slug}_*.{md,html}` (보존).
- 최종 산출물: `docs/` (사이트), `docs/data/curriculum.json`·`docs/data/qa-log.jsonl` (상태/기록).
- 클론 코드 참조 해답(선택): `clone-project/_solution/{slug}/`.

## 에러 핸들링
- 에이전트 1회 재시도 후 재실패 → 해당 산출물 없이 진행하고 site-builder가 "준비 중" placeholder, 사용자에게 누락 보고(빈 dead link 금지).
- 모듈이 커리큘럼에 없음 → architect가 확장(M8+) 여부를 사용자에게 질의(임의 생성 금지).
- 커리큘럼/사양 변경이 필요 → 먼저 `_shared/*.md`와 `curriculum.json`을 동기화하고 CLAUDE.md 변경 이력에 기록.
- 날짜 필요 작업에 날짜 미제공 → 대화의 현재 날짜를 전달(스크립트 Date.now 불가).

## 핵심 약속 (사용자 요구사항)
- **질문은 반드시 기록한다.** 학습 중 질문이 오면 답변과 함께 `qa-log.jsonl`에 남긴다. 답만 하고 지나치지 말 것.
- **복습은 실제 물었던 것 중심.** 완료 시 또는 중간 요청 시 누적 질문으로 리마인드 자료를 만든다.

## 진화 (Phase 7)
- 모듈 빌드/답변 후 개선점 피드백 기회를 제공한다("이 자료에서 고칠 부분 있나요?").
- 피드백 유형별 반영: 콘텐츠 품질→해당 스킬, 역할→에이전트 정의, 순서→이 오케스트레이터, 트리거 누락→description. 모든 변경은 CLAUDE.md 변경 이력에 기록.

## 테스트 시나리오
- **정상 흐름**: 사용자 "1강 배우자" → Phase 0(초기) → 팀 빌드 → `docs/modules/01-llm-basics.html` 생성 + curriculum.json done + 미리보기 안내.
- **질문 기록**: 학습 중 "context window가 정확히 뭐야?" → tutor 답변 + qa-log append(module=현재) → site에 반영.
- **복습 흐름**: "지금까지 한 거 복습" → tutor가 qa-log+완료 모듈로 `docs/reviews/review-{날짜}.html` 생성.
- **에러 흐름**: clone-mentor 2회 실패 → site-builder가 클론 섹션 placeholder + 사용자에 누락 보고.

> 상세 팀 호출 형태·배포 절차는 `references/orchestration-flow.md`, `references/deploy-github-pages.md` 참조.
