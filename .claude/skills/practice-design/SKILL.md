---
name: practice-design
description: >-
  한 모듈의 "직접 사용해보기" 실습 섹션을 집필하는 절차. 학습자가 직접 타이핑해 즉시 돌려보는 작은 Python 코드와
  단계·기대 출력·에러 해결을 만든다. "실습 자료/사용해보기" 및 모듈 빌드의 실습 단계에서 사용. practice-designer 에이전트가 사용.
---

# 실습 설계 (practice-design)

## 먼저 읽을 것
- `_workspace/{slug}_spec.md`, `_shared/content-conventions.md`, `_shared/claude-api-cheatsheet.md`.

## 설계 원칙
- **직접 타이핑 → 즉시 실행**. 코드는 import·키 설정 포함 그대로 돌아가야 한다.
- 한 실습 = 한 개념의 최소 확인(5~30줄). 큰 건 여러 작은 블록으로.
- 실습은 가벼운 sandbox(클론과 별개 파일). 단 같은 개념을 다뤄 클론으로 이어지게.
- Claude API는 cheatsheet 그대로. 작은 `max_tokens`로 비용 감각. 키 노출 금지.

## 한 실습 블록의 구성
1. **무엇을/왜**(1~2줄) → 2. **코드**(`<pre><code class="language-python">`) → 3. **실행**(`<pre><code class="language-bash">`) → 4. **기대 출력**(`<pre class="output">`) → 5. **막히면**(흔한 에러 1~3개와 해결).

## 모듈별 실습 소재(스펙의 running example 사용; 참고 기본값)
- M0: 첫 `messages.create` 1회 + 같은 질문 2회로 stateless 체험.
- M1: history 누적 멀티턴 + system으로 말투 변경 + `messages.stream`.
- M2: `get_weather`(가짜) 도구 1개 → tool_use/tool_result 1왕복.
- M3: 계산기 도구로 멀티스텝 미니 루프(while + stop_reason).
- M4: 토큰 추정 + 오래된 메시지 요약 치환(미니 compaction).
- M5: "plan 먼저" + 위험 도구 confirm 게이트.
- M6: 순수 파이썬 코사인 유사도로 작은 문서 검색 → "검색해 답하기".
- M7: 통합 데모 시나리오 1개 + 로그 살펴보기.

## HTML 형식 (조각)
```html
<section class="module-section" id="practice">
  <h2>직접 사용해보기</h2>
  <p class="hint">아래 코드를 직접 타이핑해 실행해 보세요. (전제: Python 3.10+, ANTHROPIC_API_KEY 설정)</p>
  <h3>1) …</h3>
  <pre><code class="language-python">…</code></pre>
  <pre><code class="language-bash">python step1.py</code></pre>
  <pre class="output">…기대 출력…</pre>
  <div class="callout warn"><strong>막히면:</strong> 401이면 키 미설정 … </div>
</section>
```
→ `_workspace/{slug}_practice.html`

## 출력 체크
- [ ] 코드 그대로 실행 가능  [ ] 기대 출력 제시  [ ] "막히면" 포함  [ ] 키/비용 주의  [ ] running example 일치
