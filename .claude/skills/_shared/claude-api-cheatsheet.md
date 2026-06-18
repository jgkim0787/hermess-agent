# Claude API 치트시트 (Python) — 학습자료용 정확 레퍼런스

> 모든 콘텐츠/클론 코드의 Claude API 사용은 **이 파일을 따른다**. 메모리로 지어내지 말 것.
> 출처: claude-api 스킬(2026-06 기준). 새 사실이 필요하면 claude-api 스킬을 다시 로드하거나 Context7로 확인.

## 모델 ID (코스 정책)

| 용도 | 모델 ID | 비고 |
|------|---------|------|
| **코스 기본값** | `claude-sonnet-4-6` | cost-효율 + 고성능, 1M context, 64K output |
| 가장 저렴/빠름 | `claude-haiku-4-5` | 단순·속도 위주 작업 |
| 최고 성능 | `claude-opus-4-8` | 어려운 추론/장기 에이전트 |

- 모델 ID 문자열은 **있는 그대로** 사용. 날짜 suffix 붙이지 말 것(`claude-sonnet-4-6` ✅, `claude-sonnet-4-6-20251114` ❌).
- 이 ID들이 낯설어 보여도 실제 모델이다(학습 데이터 cutoff 이후 출시). 임의로 `claude-3-...` 등으로 바꾸지 말 것.

## 설치 / 인증

```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-..."   # 코드에 키 하드코딩 금지
```

```python
import anthropic
client = anthropic.Anthropic()   # ANTHROPIC_API_KEY 환경변수 자동 사용
```

## 기본 호출 (messages.create)

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "프랑스의 수도는?"}
    ],
)
# response.content 는 블록 리스트. .type 확인 후 .text 접근.
for block in response.content:
    if block.type == "text":
        print(block.text)
```

- `system` 프롬프트: 최상위 `system="..."` 파라미터.
- **API는 stateless**: 멀티턴은 매 호출에 전체 `messages` history를 다시 보낸다. 모델이 "기억"하는 건 우리가 history를 보내기 때문.
- `max_tokens`: 응답 최대 토큰(하드 상한). 비스트리밍 기본 권장 ~16000; 짧은 예제는 1024로 충분. 분류 등 짧은 출력은 256.
- `stop_reason`: `end_turn`(자연 종료) | `max_tokens`(상한 도달) | `tool_use`(도구 호출 원함) | `refusal`(안전상 거부) | `pause_turn`(서버툴 재개).

## 멀티턴 대화 (history 직접 관리)

```python
messages = []
def chat(user_text: str) -> str:
    messages.append({"role": "user", "content": user_text})
    resp = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=1024, messages=messages,
        system="너는 간결한 한국어 도우미야.",
    )
    answer = next((b.text for b in resp.content if b.type == "text"), "")
    messages.append({"role": "assistant", "content": answer})
    return answer
```

규칙: 첫 메시지는 `user`. consecutive same-role도 허용(합쳐짐).

## Streaming (스트리밍)

```python
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "짧은 이야기 써줘"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    final = stream.get_final_message()   # 완료 후 전체 메시지(usage 등)
```

- 긴 출력/큰 max_tokens는 스트리밍 권장(HTTP 타임아웃 회피).

## Tool Use — 도구 정의

```python
tools = [
    {
        "name": "get_weather",
        "description": "특정 도시의 현재 날씨를 반환한다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "도시 이름, 예: Seoul"}
            },
            "required": ["location"],
        },
    }
]
```

- `input_schema`는 JSON Schema. description은 **언제 쓰는지**까지 적으면 호출률↑.
- 모델은 직접 실행하지 않는다 → 응답에 `tool_use` 블록을 담아 "이 도구를 이 입력으로 불러줘"라고 요청. 우리가 실행 후 `tool_result`로 회신.

## Tool Use — 수동 agent loop (★ 클론의 심장)

```python
messages = [{"role": "user", "content": user_input}]
while True:
    resp = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=4096,
        tools=tools, messages=messages,
    )

    if resp.stop_reason == "end_turn":
        break   # 더 부를 도구 없음 → 종료

    # assistant 응답(도구 호출 포함)을 history에 그대로 append
    messages.append({"role": "assistant", "content": resp.content})

    # tool_use 블록마다 실행 → tool_result 수집
    tool_results = []
    for block in resp.content:
        if block.type == "tool_use":
            result = run_tool(block.name, block.input)   # 우리 구현
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,        # tool_use 의 id와 반드시 매칭
                "content": result,               # 문자열
                # 에러 시: "is_error": True
            })

    # tool_result 들을 user 메시지로 회신
    messages.append({"role": "user", "content": tool_results})

# 최종 텍스트
final_text = next(b.text for b in resp.content if b.type == "text")
```

핵심 규칙:
- 매 턴 `resp.content`(assistant)를 **통째로** history에 넣는다(tool_use 블록 보존).
- 각 `tool_use`에는 정확히 하나의 `tool_result`(같은 `tool_use_id`)로 답한다 — 빠지면 다음 호출이 400.
- 무한루프 방지: `max_steps` 카운터를 둔다.
- (참고) SDK엔 자동 루프 `client.beta.messages.tool_runner`(+ `@beta_tool`)도 있지만, **학습 목적상 클론은 수동 루프를 직접 구현**한다. 자동 러너는 "쉬운 길"로 소개만.

## 에러 처리(자주 만나는 것)

```python
import anthropic
try:
    resp = client.messages.create(...)
except anthropic.AuthenticationError:
    ...  # 키 누락/오타 → ANTHROPIC_API_KEY 확인
except anthropic.NotFoundError:
    ...  # 모델 ID 오타
except anthropic.RateLimitError as e:
    ...  # 429, SDK가 기본 재시도(max_retries=2)
```

흔한 입문 에러: 키 미설정(401), 모델명 오타(404), tool_result 누락/ id 불일치(400), 첫 메시지가 assistant(400).

## 비용 감각 (가르칠 때 언급)

- 과금은 input/output **토큰** 기준. sonnet-4-6 = $3 / $15 per 1M tokens(in/out). 멀티턴은 history 누적이라 토큰이 빠르게 는다 → M4 메모리 압축의 동기.
- 토큰 정확 측정: `client.messages.count_tokens(model=..., messages=...)`. (tiktoken 쓰지 말 것 — Claude용 아님.)
