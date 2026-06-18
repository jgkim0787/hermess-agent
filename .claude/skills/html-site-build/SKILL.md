---
name: html-site-build
description: >-
  콘텐츠 조각(개념/실습/클론 HTML)을 모듈 페이지로 조립하고 docs/ 학습 사이트(GitHub Pages)의 index·내비게이션·
  데이터를 갱신하는 절차. "사이트 갱신/페이지 조립/미리보기/배포", 모듈 빌드의 조립 단계, 데이터 렌더에 사용. site-builder 에이전트가 사용.
---

# 사이트 빌드 (html-site-build)

## 먼저 읽을 것
- `_shared/content-conventions.md`(HTML 형식), `assets/module-template.html`(이 스킬의 모듈 템플릿), `docs/data/curriculum.json`.

## 사이트 구조
```
docs/
├── .nojekyll                 # Jekyll 비활성(보존)
├── index.html                # 홈/로드맵 (curriculum.json fetch 렌더)
├── assets/{style.css, app.js}# 디자인/동작 (사이드바·코드복사·데이터 렌더)
├── data/{curriculum.json, qa-log.jsonl}  # 상태/기록 (사이트가 fetch)
├── modules/{slug}.html       # 모듈 페이지
├── qa/index.html             # 질문 모음
└── reviews/review-*.html     # 복습 페이지
```

## 모듈 페이지 조립
1. `assets/module-template.html`을 읽어 placeholder를 치환:
   - `{{TITLE}}` 모듈 제목, `{{SLUG}}` slug, `{{ORDER}}` 번호
   - `{{CONCEPT}}` ← `_workspace/{slug}_concept.html`
   - `{{PRACTICE}}` ← `_workspace/{slug}_practice.html`
   - `{{CLONE}}` ← `_workspace/{slug}_clone.html`
   - `{{PREV_HREF}}/{{PREV_TITLE}}/{{NEXT_HREF}}/{{NEXT_TITLE}}` ← curriculum.json 순서
2. 조각이 없으면 그 자리에 `<section class="module-section"><p class="hint">준비 중입니다.</p></section>` placeholder를 넣고 오케스트레이터에 누락 보고(빈 dead link 금지).
3. `docs/modules/{slug}.html`로 저장.
4. `docs/data/curriculum.json`에서 이 모듈 `status="done"`.
5. 코드 블록은 `<pre><code class="language-*">` 형태여야 app.js의 highlight+copy가 동작한다. 어긋난 조각은 교정.

## 데이터 렌더(페이지 재생성 불필요)
- `index.html`/모듈 사이드바/qa/review는 런타임에 `app.js`가 `data/*.json(l)`을 fetch해 렌더한다. 따라서 **질문/상태만 바뀐 경우 데이터 파일만 갱신**하면 된다(HTML 재생성 X).
- qa-log.jsonl은 JSONL(줄당 1 JSON). 모듈 페이지의 "이번 모듈 질문"은 app.js가 `module==slug` 항목을 필터해 보여준다.

## 경로/배포 규칙
- GitHub Pages 프로젝트 페이지 base = `/{repo}/`. 내부 링크는 **상대경로**(`../assets/`, `./modules/…`).
- `docs/.nojekyll` 유지. 비밀(.env)은 docs에 두지 않는다.
- 미리보기: `python -m http.server 8000 -d docs`.

## 출력 체크
- [ ] 템플릿 placeholder 모두 치환  [ ] 누락 섹션 placeholder+보고  [ ] curriculum.json done  [ ] 상대경로  [ ] 코드 클래스 정확  [ ] 미리보기 정상
