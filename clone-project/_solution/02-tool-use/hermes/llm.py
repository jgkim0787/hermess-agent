# hermes/llm.py
import anthropic
from .config import MODEL, MAX_TOKENS
from .tools import TOOLS, run_tool

client = anthropic.Anthropic()   # ANTHROPIC_API_KEY 환경변수 사용

SYSTEM = "너는 Hermes라는 간결한 한국어 도우미야. 군더더기 없이 핵심만 답한다."


def ask(prompt: str) -> str:
    """단발 질문 → 답변 텍스트. 아직 기억도 도구도 없는 'Hermes의 두뇌'."""
    resp = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in resp.content if b.type == "text")


def chat(messages: list) -> str:
    """history(messages 리스트)를 받아 호출하고, 답변 텍스트를 반환한다.
    stateless API라 매 호출에 전체 history를 다시 보낸다 — 이 messages가 곧 '기억'."""
    resp = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM,            # persona는 messages가 아니라 별도 슬롯
        messages=messages,        # 전체 history를 통째로 전송
    )
    return "".join(b.text for b in resp.content if b.type == "text")


def stream_chat(messages: list) -> str:
    """history를 받아 token을 흘려 출력하고, 완성된 전체 답변 텍스트를 반환한다."""
    chunks = []
    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:   # token이 오는 대로
            print(text, end="", flush=True)
            chunks.append(text)
    print()                                # 줄바꿈 마무리
    return "".join(chunks)                 # history에 append 하려고 모아서 반환


def chat_with_tools(messages: list) -> str:
    """도구를 쓸 수 있는 한 턴. 도구 1-step 왕복까지만 (while 아님 — M3의 씨앗).
    messages 에는 이미 이번 user 입력이 들어 있다고 가정하고, 이 안에서
    assistant/tool_result 턴을 append 한 뒤 최종 답변 텍스트를 반환한다."""
    # ── 1차 호출: M1과 달리 tools=TOOLS 를 함께 보낸다 (모델이 도구 존재를 알게) ──
    resp = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM,
        tools=TOOLS,
        messages=messages,
    )

    # ① 모델이 도구를 안 부르고 그냥 답했으면(end_turn 등) 여기서 끝 — M1의 chat 과 같은 경로.
    if resp.stop_reason != "tool_use":
        messages.append({"role": "assistant", "content": resp.content})
        return "".join(b.text for b in resp.content if b.type == "text")

    # ② 도구를 부르고 싶어 멈췄다. assistant 응답을 '통째로' history에 넣는다
    #    (tool_use 블록을 보존해야 다음 호출이 맥락을 안다).
    messages.append({"role": "assistant", "content": resp.content})

    # ③ tool_use 블록마다 실제 함수를 실행하고 결과를 tool_result 로 모은다.
    tool_results = []
    for block in resp.content:
        if block.type == "tool_use":
            result = run_tool(block.name, block.input)   # 우리가 실행
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,   # 같은 id로 '이 요청에 대한 답'임을 매칭
                "content": result,          # 반드시 문자열
            })

    # ④ 도구 결과를 user 턴으로 회신한다 (history에 append — M1 stateless 그대로).
    messages.append({"role": "user", "content": tool_results})

    # ── 2차 호출: 결과가 담긴 messages를 통째로 다시 보낸다 → 이번엔 최종 답변(end_turn) ──
    resp2 = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM,
        tools=TOOLS,
        messages=messages,
    )
    messages.append({"role": "assistant", "content": resp2.content})
    return "".join(b.text for b in resp2.content if b.type == "text")
