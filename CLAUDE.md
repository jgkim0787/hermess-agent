# CLAUDE.md

## 하네스: AI Agent 입문 학습 지도 (Hermes 과정)

**목표:** 전문 SW 개발자에게 AI Agent를 입문 수준으로 가르친다 — 개념 설명 + 직접 실습 + 복제 프로젝트(Hermes)를 HTML 학습 사이트(GitHub Pages, `docs/`)로 제공하고, 학습 중 질문을 답변·기록하며 복습 자료를 생성한다.

**트리거:** 이 과정과 관련된 요청(학습/N강/다음 강의/모듈/개념·실습·복제 자료/Hermes/질문 기록/복습·리마인드/사이트 갱신·배포/커리큘럼) 및 그 후속(다시/재실행/이어서/보완)에는 `learning-harness` 스킬을 사용한다. 단순 사실 질문은 직접 답해도 되며, 학습 관련이면 답 후 `learning-tutor`로 기록한다.

**구성 요약(상세는 `.claude/`):** 에이전트 팀 = `curriculum-architect` · `concept-lecturer` · `practice-designer` · `clone-mentor` · `site-builder` · `learning-tutor`. 실행 모드 = 하이브리드(모듈 빌드는 에이전트 팀, 단발 작업은 단일 서브). 모든 Agent 호출은 `model: "opus"`.

**공유 진실 파일:** `.claude/skills/_shared/{curriculum.md, hermes-spec.md, content-conventions.md, claude-api-cheatsheet.md}`. 커리큘럼/사양 변경 시 이 파일들과 `docs/data/curriculum.json`을 동기화하고 아래 이력에 기록한다.

**변경 이력:**
| 날짜 | 변경 내용 | 대상 | 사유 |
|------|----------|------|------|
| 2026-06-17 | 초기 구성(에이전트 6 · 스킬 8 · 사이트 셸 · Module 0 worked example) | 전체 | - |
| 2026-06-18 | GitHub Pages 배포 (public, main /docs → https://jgkim0787.github.io/hermess-agent/) | docs/ | 인터넷 접근 |
