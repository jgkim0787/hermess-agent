# 오케스트레이션 상세 흐름

## 모듈 빌드 — 팀 호출 형태(개념)

```
1) TeamCreate(team="hermes-build", members=[
     curriculum-architect, concept-lecturer, practice-designer, clone-mentor, site-builder
   ])  # 모두 model:"opus"

2) TaskCreate:
   - T1 architect: "{slug} 모듈 스펙 작성 → _workspace/{slug}_spec.md, curriculum.json in_progress"
   - T2 concept   (depends T1): "_workspace/{slug}_concept.html"
   - T3 practice  (depends T1): "_workspace/{slug}_practice.html"
   - T4 clone     (depends T1): "_workspace/{slug}_clone.html"
   - T5 site      (depends T2,T3,T4): "docs/modules/{slug}.html 조립 + index/curriculum.json done"

3) T2/T3/T4는 병렬. 세 에이전트는 SendMessage로 running example·용어 합의.
4) 리더(오케스트레이터)는 진행 모니터링 → 완료 후 미리보기 안내 → 팀 정리.
```

서브 에이전트로 단순화해도 되는 경우(팀 통신이 불필요할 때): architect를 먼저 1회 호출해 스펙을 만들고, 이후 `Agent(run_in_background=true)`로 concept/practice/clone을 병렬 호출, 마지막에 site-builder. 단 콘텐츠 3인방의 일관성 조율이 필요하면 팀을 쓰는 편이 품질이 높다.

## "다음 모듈" 결정
1. `docs/data/curriculum.json` 로드.
2. `status == "in_progress"`가 있으면 그 모듈을 이어서.
3. 없으면 `status == "planned"` 중 최소 `order`.
4. 모두 `done`이면 사용자에게 복습 또는 확장(M8+)을 제안.

## 부분 재실행
- "개념만 다시" → concept-lecturer만 재호출(기존 `_concept.html` 읽어 개선) → site-builder 재조립.
- "이 코드가 안 돌아가" → 해당 섹션 담당(practice 또는 clone)만 + site-builder.
- 데이터만 변경(질문/상태) → site-builder만(페이지 데이터 재렌더), 콘텐츠 에이전트 미호출.

## 질문 기록 흐름(단일 서브)
```
Agent(subagent_type="learning-tutor", model="opus",
      prompt="질문: <원문>. 현재 모듈=<slug 또는 general>. 오늘 날짜=<YYYY-MM-DD>.
              claude-api-cheatsheet와 모듈 콘텐츠에 근거해 답하고 qa-log.jsonl에 append.")
→ 이어서 site-builder로 qa 페이지/모듈 '이번 질문' 렌더(선택, 묶어서).
```

## 복습 흐름(단일 서브)
```
Agent(subagent_type="learning-tutor", model="opus",
      prompt="review-generation: qa-log + 완료 모듈로 docs/reviews/review-<YYYYMMDD>.html 생성.
              실제 물었던 질문 중심, 약점 추정, 다음 추천. 오늘 날짜=<YYYY-MM-DD>.")
```

## 워크스페이스 규약
- `_workspace/{slug}_spec.md|_concept.html|_practice.html|_clone.html`
- 보존(삭제 금지) — 부분 재실행·감사·복습 근거.
- 최종만 `docs/`로. `docs/data/*`는 사이트가 fetch하는 상태/기록.
