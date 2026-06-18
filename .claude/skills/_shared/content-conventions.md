# 콘텐츠 작성 규약 (모든 콘텐츠 에이전트 공통)

> `concept-lecturer`, `practice-designer`, `clone-mentor`, `site-builder`가 공유하는 톤·형식 규약.
> 각 스킬은 이 파일을 읽고 따른다. 일관성(같은 running example·같은 용어·같은 HTML 형식)이 품질의 핵심.

## 1. 언어와 톤

- **한글**로 쓴다. 전문 용어는 **영어 원어 그대로**(번역·음차 금지): `token`, `prompt`, `tool use`, `agent loop`, `ReAct`, `context window`, `embedding`, `stop_reason` 등.
- 독자는 **전문 SW 개발자**다. 일반 SW 개념(HTTP, JSON, 재귀, 상태머신, 스레드, 캐시…)은 설명 없이 쓴다. 장황한 기초 설명은 금지.
- **단, AI Agent 개념은 입문자** 취급. agent 관련 용어는 **첫 등장 시 한 문장 정의**를 붙인다. 예: "`tool use` — LLM이 직접 실행하지 못하는 작업을, 정해진 함수(도구)를 '호출해 달라'고 요청하는 메커니즘."
- 문체: 명료한 평서/설명체. 과장·격려 남발 금지("놀랍게도!" 류 X). 군더더기 없이.

## 2. analogy(비유)를 적극 쓴다

aware한 SW 개념에 빗대면 입문 개념이 빨리 박힌다. 예시:
- LLM = **stateless 순수 함수**(텍스트 in → 텍스트 out, 부작용·기억 없음)
- agent loop = 함수 호출을 감싼 **REPL / 이벤트 루프**(부작용=도구, 피드백=관찰)
- tool calling = LLM이 내는 **RPC 요청**(우리가 서버처럼 실행해 응답)
- context window = 함수의 **입력 버퍼 한도**
- system prompt = 프로세스의 **환경설정/불변 규칙**
- RAG = **외부 캐시/DB 조회 후 프롬프트에 주입**

비유는 정확해야 한다. 틀린 비유는 안 하느니만 못함 — 한계가 있으면 한 줄로 짚는다.

## 3. 정확성

- Claude API 코드·모델 ID·tool use 형식은 **`claude-api-cheatsheet.md`를 그대로 따른다**. 추측 금지.
- 커리큘럼·모듈 범위는 `curriculum.md`, 클론 사양은 `hermes-spec.md`를 따른다.
- 모든 코드 예제는 **그대로 복붙해 돌아가야 한다**(import·키 설정 포함, 생략 시 명시).

## 4. 모듈 HTML 조각(fragment) 형식

각 콘텐츠 에이전트는 자기 섹션을 **HTML 조각**으로 만들어 `site-builder`에 넘긴다(또는 site-builder가 템플릿에 끼운다). 조각 규약:

- 섹션 루트는 `<section class="module-section" id="...">`.
- 제목 단계: 모듈 제목 `<h1>`은 site-builder가 처리. 콘텐츠는 `<h2>`(섹션), `<h3>`(소제목)부터.
- 코드 블록은 반드시:
  ```html
  <pre><code class="language-python">… 코드 …</code></pre>
  ```
  (highlight.js + copy 버튼이 자동 적용된다. 언어 클래스 필수: `language-python`, `language-bash`, `language-json`.)
- 실행/터미널 출력은 `language-bash` 또는 `<pre class="output">`.
- 콜아웃(callout) 박스 클래스: `callout note`(정의/팁), `callout warn`(주의/함정), `callout why`(왜 그런가). 예:
  ```html
  <div class="callout note"><strong>정의 — token:</strong> 모델이 텍스트를 다루는 최소 단위 …</div>
  ```
- "직접 타이핑" 실습 코드 블록에는 `data-typeit` 속성 대신 평범한 `<pre><code>`를 쓰되, 실습 섹션 상단에 "아래 코드를 직접 타이핑해 보세요" 안내.

## 5. 모듈 페이지의 3요소 구성

site-builder가 한 모듈 페이지를 조립할 때 순서:
1. `## 개념` — concept-lecturer 산출
2. `## 직접 사용해보기` — practice-designer 산출(타이핑 실습 코드)
3. `## Hermes 만들기` — clone-mentor 산출(클론 증분)
4. (자동) `## 이번 모듈 질문` — 해당 모듈 태그의 qa-log 항목(있으면)
5. (자동) 이전/다음 모듈 내비게이션

## 6. running example 일관성

한 모듈 안에서 개념→실습→클론이 **같은 소재**를 쓰면 이해가 빠르다. 모듈 spec의 예시를 따르고, 새로 만들면 세 에이전트가 같은 예시를 공유하도록 `curriculum-architect`의 모듈 스펙에 running example을 한 줄 적어 둔다.

## 7. 분량

- 한 모듈 페이지는 **한 자리에서 학습 가능한 분량**(개념 5~10분, 실습 10~20분, 클론 15~30분)이 목표.
- 개념 섹션이 너무 길면 핵심만. 깊은 곁가지는 `callout` 또는 "더 알아보기" 링크로.

## 8. 접근성/실용

- 코드에 한글 주석 OK. 변수/함수명은 영어.
- 외부 이미지 의존 최소(오프라인에서도 보이게). 다이어그램이 필요하면 간단한 ASCII/박스 또는 인라인 SVG.
- 모든 페이지는 모바일에서도 읽혀야 한다(site-builder의 CSS가 처리).
