---
name: concept-writing
description: >-
  한 모듈의 "주요 개념 설명" 섹션을 한글 HTML 조각으로 집필하는 절차. 전문 개발자 대상이되 AI Agent 용어는
  입문자 수준으로 정의하고 analogy로 설명한다. "개념 설명/개념 자료" 및 모듈 빌드의 개념 단계에서 사용.
  concept-lecturer 에이전트가 사용.
---

# 개념 집필 (concept-writing)

## 먼저 읽을 것
- `_workspace/{slug}_spec.md` (모듈 스펙), `_shared/content-conventions.md` (톤·HTML·analogy), `_shared/claude-api-cheatsheet.md` (API 정확성).

## 작성 절차
1. 스펙의 **개념 목표**와 **정의할 용어**를 체크리스트로 잡는다. 용어는 빠짐없이 첫 등장 시 정의.
2. 도입(1문단): 이 개념이 **왜 필요한가**를 직전 모듈/문제 상황과 연결. 동기 없이 정의부터 던지지 않는다.
3. 핵심 전개: 한 개념씩. 각 개념마다 — ① 정의(callout note) ② SW 개발자가 아는 것에 빗댄 analogy ③ 동작 방식 ④ (필요시) 최소 코드/도식.
4. running example을 스펙대로 사용(실습·클론과 동일 소재).
5. "왜 그런가"는 `callout why`로, 함정/오해는 `callout warn`로.
6. 마무리: **"한눈 정리"** 핵심 3~5줄.

## analogy 가이드 (정확하게)
- LLM = stateless 순수 함수 / agent loop = REPL·이벤트 루프 / tool calling = RPC / context window = 입력 버퍼 한도 / system prompt = 불변 설정 / RAG = 캐시·DB 조회 후 주입.
- 비유의 **한계**가 있으면 한 줄로 짚는다(틀린 비유는 금지).

## HTML 형식 (조각)
```html
<section class="module-section" id="concept">
  <h2>개념</h2>
  <p>…동기…</p>
  <div class="callout note"><strong>정의 — tool use:</strong> …</div>
  <h3>…</h3>
  <pre><code class="language-python">…</code></pre>
  <div class="callout why"><strong>왜?</strong> …</div>
  <h3>한눈 정리</h3>
  <ul><li>…</li></ul>
</section>
```
→ `_workspace/{slug}_concept.html`

## 금지 / 주의
- 일반 SW 기초(HTTP/JSON/재귀 등) 설명 금지. agent 개념에만 지면.
- API 코드/모델 ID는 cheatsheet를 그대로. 불확실하면 명시(추측 금지).
- 분량 5~10분. 곁가지는 callout/"더 알아보기"로.

## 출력 체크
- [ ] 정의할 용어 전부 정의  [ ] analogy 1+  [ ] running example 일치  [ ] 한눈 정리  [ ] 코드 클래스 정확(language-*)
