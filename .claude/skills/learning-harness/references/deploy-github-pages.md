# GitHub Pages 배포 가이드

학습 사이트는 `docs/`에 정적 HTML로 빌드된다. GitHub Pages의 "/docs 폴더" 옵션으로 바로 호스팅한다.

## 로컬 미리보기 (배포 전 항상)
```bash
python -m http.server 8000 -d docs
# 브라우저: http://localhost:8000/   (홈)
#          http://localhost:8000/modules/00-what-is-an-agent.html
```

## 최초 1회 — 저장소 + Pages 설정
> 외부 공개(публиш) 동작이므로 **사용자 승인 후** 진행한다. 키/비공개 정보가 docs에 없는지 먼저 확인.

```bash
# 저장소 루트에서
git init
git add -A
git commit -m "Hermes 학습 과정: 초기 사이트"

# GitHub 저장소 생성 + 푸시 (gh CLI 사용; 비공개로 시작 권장)
gh repo create hermess-agent --private --source=. --push
# 또는 공개로: gh repo create hermess-agent --public --source=. --push
```

GitHub에서 Pages 켜기:
```bash
# main 브랜치의 /docs 를 소스로 설정 (gh api)
gh api -X POST repos/{owner}/hermess-agent/pages \
  -f "source[branch]=main" -f "source[path]=/docs" 2>/dev/null || \
echo "이미 설정됐거나 권한 필요 — 웹: Settings → Pages → Source: main /docs"
```
또는 웹 UI: **Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: main /docs → Save.**

배포 URL(프로젝트 페이지): `https://{owner}.github.io/hermess-agent/`
- 그래서 사이트 내부 링크는 **상대경로**여야 한다(base가 `/hermess-agent/`).
- `docs/.nojekyll`을 둬서 Jekyll 처리를 끈다(`_`로 시작하는 경로 등 보존).

## 이후 갱신
```bash
git add -A && git commit -m "모듈 추가: {slug}" && git push
# 1~2분 뒤 https://{owner}.github.io/hermess-agent/ 에 반영
```

## 비공개 학습 자료라면
- 저장소를 `--private`로. 단 GitHub Pages는 무료 플랜에서 private repo의 Pages를 공개 URL로 노출할 수 있으니, 민감하지 않은 학습 자료만 둔다.
- 완전 비공개로 보려면 로컬 `http.server`만 사용해도 충분하다(인터넷 접근만 포기).

## 체크리스트
- [ ] `docs/.nojekyll` 존재
- [ ] 모든 링크 상대경로(`./`, `../`)
- [ ] `ANTHROPIC_API_KEY` 등 비밀이 docs/clone-project에 커밋되지 않음(`.env`는 `.gitignore`)
- [ ] 로컬 미리보기로 모듈/홈/qa/review 페이지 정상 확인
