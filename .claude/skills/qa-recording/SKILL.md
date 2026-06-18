---
name: qa-recording
description: >-
  학습 중 사용자 질문에 정확히 답하고, 그 Q&A를 qa-log.jsonl에 구조화해 기록하는 절차. 학습 과정에서 떠오른
  질문("왜 …야?", "이 코드 의미는?", "… 차이가 뭐야?")에 사용. 답변과 동시에 반드시 기록한다. learning-tutor 에이전트가 사용.
---

# 질문 답변 + 기록 (qa-recording)

이 과정의 **핵심 요구사항**: 질문에 답하고 그 내용을 빠짐없이 기록한다. 답만 하고 지나치지 말 것.

## 먼저 읽을 것
- `_shared/claude-api-cheatsheet.md`, 관련 모듈 콘텐츠(`docs/modules/{slug}.html`), `docs/data/qa-log.jsonl`(이전 질문 일관성).

## 답변 절차
1. 현재 모듈 맥락을 활용해 한글로 정확히 답한다(전문 용어 영어 유지).
2. 근거는 cheatsheet/모듈 콘텐츠. 불확실하면 "확실치 않음"을 밝힌다(추측 단정 금지).
3. 너무 길게 늘어놓지 말고 질문에 정조준. 필요하면 관련 모듈/개념으로 연결.

## 기록 절차 (필수) → `docs/data/qa-log.jsonl` 에 **append 한 줄**
JSON 한 줄(JSONL). 필드:
```json
{"ts":"<YYYY-MM-DD, 오케스트레이터 제공>","module":"<slug 또는 general>",
 "question":"<사용자 원문>","answer_summary":"<2~4줄 요지>",
 "tags":["<개념 키워드>"],"concepts":["<연결 모듈/용어>"]}
```
규칙:
- **append-only**. 기존 줄 수정/삭제 금지(정정은 새 줄로, tags에 "correction").
- `module`은 질문 시점의 모듈 slug. 불명확하면 "general".
- `tags`/`concepts`는 복습·약점 분석의 근거가 되니 성실히 채운다.
- 날짜는 스크립트로 생성하지 말고 오케스트레이터가 준 현재 날짜를 쓴다.

## 렌더 연동
- 기록 후 site-builder가 `docs/qa/index.html`와 모듈 페이지의 "이번 모듈 질문"을 재렌더하도록 신호한다(또는 오케스트레이터가 묶어 호출).

## 출력 체크
- [ ] 정확한 답변 제공  [ ] qa-log.jsonl 에 유효한 JSON 한 줄 append  [ ] module/tags 채움  [ ] append-only 준수
