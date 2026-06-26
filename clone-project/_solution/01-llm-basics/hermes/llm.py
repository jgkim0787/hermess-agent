# hermes/llm.py
import anthropic
from .config import MODEL, MAX_TOKENS

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
