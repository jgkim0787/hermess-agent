# hermes/agent.py
"""Hermes 본체 — agent loop(ReAct)를 담은 class Hermes.

M2 llm.chat_with_tools 의 도구 1-step 왕복(if)을 while 루프로 '승격'한 것.
도구 왕복 4단계·tool_use_id 매칭은 M2와 완전히 동일하고, 그 왕복을
'stop_reason 이 tool_use 가 아닐 때까지 반복'으로 감쌌을 뿐이다."""
from .llm import client, SYSTEM
from .config import MODEL, MAX_TOKENS, MAX_STEPS
from .tools import TOOLS, run_tool


class Hermes:
    def __init__(self):
        # 대화 history를 Hermes가 소유한다 (M2에선 __main__의 지역변수 messages였다).
        # 이 self.messages 가 M4에서 Memory 객체로 교체될 자리다.
        self.messages = []

    def run(self, user_msg: str) -> str:
        """user_msg를 받아, stop_reason이 tool_use가 아닐 때까지 도구를 반복 실행한다.
        while 한 바퀴 = ReAct 한 사이클(추론→행동→관찰). MAX_STEPS로 무한 루프를 막는다."""
        self.messages.append({"role": "user", "content": user_msg})

        step = 0
        while step < MAX_STEPS:                 # ← M2의 if를 감싼 while + 무한 루프 가드
            step += 1
            # 매 스텝: 커진 history 전체를 통째로 재전송(M1 stateless 그대로).
            resp = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM,
                tools=TOOLS,
                messages=self.messages,
            )
            # assistant 응답을 '통째로' append (tool_use 블록 보존).
            # M2에선 두 분기에 각각 있던 걸, 여기선 루프 상단 1회로 합쳤다.
            self.messages.append({"role": "assistant", "content": resp.content})

            # 종료 분기 — M2 chat_with_tools의 '그 테스트' 그대로.
            # tool_use가 아니면(end_turn/max_tokens/refusal) 최종 답으로 종료.
            if resp.stop_reason != "tool_use":
                return "".join(b.text for b in resp.content if b.type == "text")

            # 여기부터는 M2와 '완전히 동일' — tool_use 블록마다 실행해 tool_result 수집.
            tool_results = []
            for block in resp.content:
                if block.type == "tool_use":
                    print(f"  ↳ step {step}: {block.name}({block.input})")  # 루프가 도는 걸 눈으로
                    result = run_tool(block.name, block.input)   # 우리가 실행
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,   # tool_use 의 id와 반드시 매칭
                        "content": result,          # 반드시 문자열
                    })
            # 결과를 user 턴으로 회신하고 루프 top으로 → M2의 '2차 호출'을 루프가 대체.
            self.messages.append({"role": "user", "content": tool_results})

        # MAX_STEPS까지 돌아도 안 끝났다 → 강제 종료(가드 탈출).
        return "[max_steps 도달 — 루프를 강제 종료했어요]"
