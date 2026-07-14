# hermes/llm.py
import anthropic
from .config import MODEL, MAX_TOKENS

client = anthropic.Anthropic()   # ANTHROPIC_API_KEY 환경변수 사용

# M5: persona(말투) 뒤에 '행동 정책' 두 문단이 붙었다 — system은 history 밖 항구 규칙이라
# compaction(M4)에도 안 사라지므로 정책을 두기 좋은 자리다.
# ⚠️ 단, 이건 '부탁'이다. 모델이 안 지킬 수도 있다. 강제는 코드가 한다 —
#    agent.py의 승인 게이트(DANGEROUS_TOOLS)가 진짜 guardrail이다.
SYSTEM = """너는 Hermes라는 간결한 한국어 도우미야. 군더더기 없이 핵심만 답한다.

여러 단계가 필요한 목표를 받으면, 가장 먼저 update_plan 도구로 계획(단계 목록)을 세운 뒤 실행을 시작한다.
계획이 바뀌면 update_plan을 다시 호출해 갱신한다.
write_file·run_bash처럼 되돌리기 어려운 도구는 사용자 승인이 필요하다. 거부당하면 같은 도구를 억지로
다시 부르지 말고, 다른 방법을 찾거나 사용자에게 무엇을 원하는지 물어본다."""


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


# M2의 chat_with_tools(도구 1-step 왕복, if)는 M3에서 agent.py::Hermes.run 의
# while 루프로 '승격'되어 이 파일에서 제거되었다. llm.py 는 M0~M1 기본기
# (client·SYSTEM·ask·chat·stream_chat)만 유지한다.
