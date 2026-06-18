# 🛰️ Hermes 과정 — AI Agent 입문 (전문 개발자용)

전문 SW 개발자가 **AI Agent**를 입문 수준에서 익히는 자기주도 학습 프로젝트.
각 모듈은 **개념 설명 → 직접 사용해보기(실습) → 복제 프로젝트(Hermes) 만들기** 3단계로 구성되며,
학습 자료는 HTML 사이트(`docs/`, GitHub Pages)로 제공된다. 학습 중 질문은 자동 기록되고, 복습(리마인드) 자료를 생성할 수 있다.

> 스택: Python + Anthropic Claude API · 언어: 한글(전문 용어는 영어)

## 무엇이 들어있나

| 경로 | 내용 |
|------|------|
| `docs/` | 학습 사이트(GitHub Pages). 홈/로드맵, 모듈 페이지, 질문 모음, 복습. |
| `docs/data/curriculum.json` | 커리큘럼·진행 상태(사이트가 fetch해 렌더). |
| `docs/data/qa-log.jsonl` | 학습 중 질문 기록(append-only). |
| `clone-project/` | 직접 타이핑해 만드는 미니 에이전트 **Hermes** 작업 폴더. |
| `.claude/` | 학습 하네스(에이전트 팀 + 스킬). Claude Code가 자료를 생성·관리한다. |

## 학습 시작

1. **사이트 보기** (로컬):
   ```bash
   python -m http.server 8000 -d docs
   # http://localhost:8000/  → 0강 "AI Agent란 무엇인가" 부터
   ```
2. **다음 강의 만들기**: Claude Code 세션에서 — `"다음 강의 배우자"` 또는 `"2강 만들어줘"`.
3. **질문하기**: 학습 중 떠오른 질문을 물으면 답변 + 자동 기록.
4. **복습**: `"지금까지 한 거 복습하자"` → 그동안의 질문으로 리마인드 자료 생성.

## 커리큘럼 (집중 입문 ~8모듈)

0. AI Agent란 무엇인가 · 1. LLM 다루기 · 2. Tool Use · 3. The Agent Loop ·
4. Memory & Context · 5. Planning & Autonomy · 6. RAG & Knowledge · 7. Hermes 완성

## 인터넷에 올리기 (GitHub Pages)

`.claude/skills/learning-harness/references/deploy-github-pages.md` 참고. 요지:
저장소 푸시 → Settings → Pages → Source: `main` `/docs` → `https://<owner>.github.io/hermess-agent/`.

---
🤖 학습 하네스로 생성·관리됩니다. 자세한 운영은 `CLAUDE.md` 참고.
