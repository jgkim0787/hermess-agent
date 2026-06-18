# Hermes — 복제 프로젝트

이 폴더는 학습자가 **직접 타이핑하며 만들어 가는** 미니 AI 에이전트 **Hermes**의 작업 공간입니다.
학습 사이트의 각 모듈 "Hermes 만들기" 섹션을 따라 파일을 한두 개씩 추가/확장하세요.

- 목적: 완성도가 아니라 **"이해한 개념이 코드로 어떻게 구현되는가"**를 손으로 확인.
- 스택: Python 3.10+ · Anthropic Claude API.
- Hermes는 과정을 거치며 **코딩 → 자율 → RAG** 에이전트의 성격을 차례로 흡수해 마지막에 통합됩니다.

## 시작

```bash
pip install -r requirements.txt
cp .env.example .env        # .env 에 본인 ANTHROPIC_API_KEY 입력
# 또는: export ANTHROPIC_API_KEY="sk-ant-..."
```

> `.env` 는 절대 커밋하지 마세요(`.gitignore`로 제외됨). API 키를 코드에 하드코딩하지 마세요.

## 모듈별로 자라는 구조 (최종 형태)

```
hermes/
├── config.py    # 모델·상수            (M0)
├── llm.py       # Claude 호출 래퍼      (M0–M1)
├── tools.py     # 도구 정의 + 실행기    (M2–M3, M5, M6)
├── memory.py    # 대화 메모리·압축      (M4)
├── rag.py       # 임베딩·검색           (M6)
├── agent.py     # agent loop = Hermes   (M3~)
└── __main__.py  # CLI 진입점            (M0~)
```

## 실행

```bash
python -m hermes "안녕 Hermes"
```

자세한 단계는 학습 사이트의 각 모듈을 따라가세요. (로컬 미리보기: 저장소 루트에서 `python -m http.server 8000 -d docs`)
