---
name: curriculum-design
description: >-
  AI Agent 입문(Hermes) 과정의 커리큘럼/로드맵을 설계·갱신하고 한 모듈의 학습 스펙을 만드는 절차.
  "커리큘럼 보여줘/바꿔/확장", "모듈 스펙", "다음에 뭘 배우지", 모듈 빌드의 첫 단계에서 사용한다.
  curriculum-architect 에이전트가 사용.
---

# 커리큘럼 설계 (curriculum-design)

curriculum-architect가 로드맵을 유지하고 모듈 스펙을 만드는 방법.

## 먼저 읽을 것
- `_shared/curriculum.md` (모듈 정의 진실), `docs/data/curriculum.json` (상태), `docs/data/qa-log.jsonl` (사용자 약점 신호), `_shared/hermes-spec.md` (클론 단계).

## 로드맵 갱신
- curriculum.md가 기준. json은 그 사본. **항상 둘을 동기화**한다. 모듈 추가/순서변경 시 두 파일을 함께 고치고, 변경 이력 기록 필요를 오케스트레이터에 알린다.
- json 모듈 객체 필드: `order, slug, title, summary, flavor, status(planned|in_progress|done), terms(정의할 용어[]), running_example`.

## "다음 모듈" 결정
1. `in_progress` 있으면 그것. 2. 없으면 `planned` 최소 order. 3. 전부 done이면 복습/확장 제안.

## 모듈 스펙 작성 → `_workspace/{slug}_spec.md`
다음 항목을 채운다(콘텐츠 3인방이 이 한 장으로 일관 작업):
1. **메타**: 번호/slug/제목/한 줄 요약/flavor.
2. **개념 목표**: 불릿 3~6개(무엇을 이해시키나).
3. **정의할 agent 용어**: 이 모듈에서 처음 등장해 정의가 필요한 용어 목록.
4. **running example**: 개념·실습·클론이 **공유할 단일 소재** 한 줄(예: "파일 읽기 도구"). 셋의 일관성을 위해 반드시 지정.
5. **실습 목표**: 직접 타이핑할 실습이 보여줄 것 + 위 running example 적용.
6. **Hermes 클론 단계**: hermes-spec의 해당 절 요약(추가/수정할 파일·함수).
7. **이전 모듈 연결**: 무엇 위에 쌓는가.
8. **분량 가이드**: 개념/실습/클론 각 목표 시간.
9. **상태 갱신**: `curriculum.json`에서 이 모듈 `status=in_progress`.

## 커리큘럼 확장(M8+) 시
- 사용자가 "포괄 과정"을 원하면 멀티에이전트/eval 심화/guardrails·안전/MCP/managed agents 등을 추가.
- curriculum.md + curriculum.json에 모듈 추가, hermes-spec에 클론 증분 추가, CLAUDE.md 변경 이력 기록.

## 출력 체크
- [ ] `_workspace/{slug}_spec.md` 9개 항목 채움  [ ] running example 명시  [ ] 정의할 용어 나열  [ ] json 상태 갱신
