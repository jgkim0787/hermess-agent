# hermes/agent.py
"""Hermes 본체 — agent loop(ReAct)를 담은 class Hermes.

M2 llm.chat_with_tools 의 도구 1-step 왕복(if)을 while 루프로 '승격'한 것.
도구 왕복 4단계·tool_use_id 매칭은 M2와 완전히 동일하고, 그 왕복을
'stop_reason 이 tool_use 가 아닐 때까지 반복'으로 감쌌을 뿐이다.

M4: history 소유 형태를 평범한 list(self.messages)에서 self.memory(class Memory)로
교체했다. 로직이 바뀌는 건 딱 한 줄 — messages=self.memory.to_messages() — 이고,
거기서 토큰 추정이 임계를 넘으면 오래된 대화가 요약 1개로 압축(compaction)된다.

M5: 루프의 '행동(Act)' 단계 바로 앞에 승인 게이트(guardrail)를 끼우고, 계획을
'에이전트 자신의 상태'(self.plan)로 들고 있는다. 모델의 모든 행동은 예외 없이
tool_use 블록으로 나와 아래 for 문을 지나가므로, 이 길목 한 곳만 잠그면 에이전트
전체가 잠긴다. while·stop_reason 분기·self.memory·MAX_STEPS는 손대지 않았다."""
from .llm import client, SYSTEM
from .config import MODEL, MAX_TOKENS, MAX_STEPS, DANGEROUS_TOOLS   # M5: DANGEROUS_TOOLS 추가
from .tools import TOOLS, run_tool
from .memory import Memory


# M5 — 거부당했을 때 모델에게 돌려줄 '관찰(observation)' 문구.
# 그냥 "거부됨"이 아니라 '다음에 뭘 하라'까지 넣는다 — 안 그러면 모델이 같은 도구를 무한 재시도한다.
DENIED_MSG = "사용자가 이 도구 실행을 거부했습니다. 다른 방법을 찾거나 사용자에게 물어보세요."


def confirm(name: str, tool_input: dict) -> bool:
    """위험 도구 실행 '직전'에 사람에게 y/n을 묻는다 (human-in-the-loop).

    기본값은 거부([y/N]) — 되돌리기 어려운 행동의 안전한 기본값은 '안 함'이다.
    비대화형 실행(파이프/CI)에선 input()이 EOFError를 내므로 거부로 처리한다(fail-closed).
    """
    print(f"  [승인 요청] {name}({tool_input})")
    try:
        answer = input("  실행할까요? [y/N] ").strip().lower()
    except EOFError:
        return False          # 못 물어보면 '안 한다' — fail-closed
    return answer == "y"      # y 외에는 전부 거부 (그냥 Enter도 거부)


class Hermes:
    def __init__(self):
        # M3까진 self.messages = [] (평범한 list)였다. M4에서 그 자리를 Memory로 교체 —
        # 자기 크기를 알고(token_estimate) 스스로 줄이는(compact) 객체가 history를 소유한다.
        self.memory = Memory()
        # M5: 현재 계획. self.memory 옆에 나란히 놓인 '에이전트 자신의 상태'다 —
        # 바깥 세상(파일·셸)이 아니라 에이전트 내부를 바꾸므로 tools.py가 아니라 여기 산다.
        self.plan = []

    def _update_plan(self, steps: list) -> str:
        """update_plan 도구의 실체 — 부작용 없는 '상태 기록' 도구다.
        파일도 셸도 네트워크도 건드리지 않는다. 모델이 자기 생각을 밖으로 꺼내
        (externalize) 우리도 모델도 볼 수 있게 만드는 장치일 뿐 — 마법이 아니다."""
        self.plan = steps
        print(f"  [plan] {len(steps)}단계")
        for i, s in enumerate(steps, 1):
            print(f"    {i}. {s}")
        return f"계획 저장됨: {len(steps)}단계"   # 반드시 '문자열' — tool_result content 규칙(M2)

    def run(self, user_msg: str) -> str:
        """user_msg를 받아, stop_reason이 tool_use가 아닐 때까지 도구를 반복 실행한다.
        while 한 바퀴 = ReAct 한 사이클(추론→행동→관찰). MAX_STEPS로 무한 루프를 막는다."""
        self.memory.append({"role": "user", "content": user_msg})

        step = 0
        while step < MAX_STEPS:                 # ← M2의 if를 감싼 while + 무한 루프 가드
            step += 1
            # 매 스텝: history를 통째로 재전송(M1 stateless). 단, to_messages()가 그 순간
            # 토큰을 추정해 임계를 넘으면 오래된 대화를 요약 1개로 접어(compact) 돌려준다.
            resp = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM,
                tools=TOOLS,
                messages=self.memory.to_messages(),
            )
            # assistant 응답을 '통째로' append (tool_use 블록 보존).
            # M2에선 두 분기에 각각 있던 걸, 여기선 루프 상단 1회로 합쳤다.
            self.memory.append({"role": "assistant", "content": resp.content})

            # 종료 분기 — M2 chat_with_tools의 '그 테스트' 그대로.
            # tool_use가 아니면(end_turn/max_tokens/refusal) 최종 답으로 종료.
            if resp.stop_reason != "tool_use":
                return "".join(b.text for b in resp.content if b.type == "text")

            # tool_use 블록마다 실행해 tool_result 수집 — M2의 왕복 그대로.
            # M5: 다만 '행동(Act)' 바로 앞에 승인 게이트가 하나 섰다(★).
            tool_results = []
            for block in resp.content:
                if block.type == "tool_use":
                    print(f"  ↳ step {step}: {block.name}({block.input})")  # 루프가 도는 걸 눈으로

                    # ★ M5 ① 승인 게이트 — run_tool '직전'. 정책 판단이 실행 분기보다 먼저 온다.
                    if block.name in DANGEROUS_TOOLS and not confirm(block.name, block.input):
                        print("  [거부됨] 실행하지 않고, 거부 사실을 모델에게 알립니다.")
                        # ★ M5 ② 거부해도 tool_use 하나당 tool_result 하나! (M2 규칙 — 빠지면 400)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,   # tool_use 의 id와 반드시 매칭
                            "content": DENIED_MSG,     # 문자열 — '거부됨'이 하나의 관찰이 된다
                            "is_error": True,          # 실패/거부임을 알리는 필드
                        })
                        continue                       # 도구는 실행 안 함. 루프는 계속 돈다.

                    # ★ M5 ③ update_plan은 '에이전트 자신의 상태'를 바꾼다 → tools.py가 아니라 여기서.
                    if block.name == "update_plan":
                        result = self._update_plan(block.input["steps"])
                    else:
                        result = run_tool(block.name, block.input)   # 바깥 세상을 바꾸는 도구

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,   # tool_use 의 id와 반드시 매칭
                        "content": result,          # 반드시 문자열
                    })
            # 결과를 user 턴으로 회신하고 루프 top으로 → M2의 '2차 호출'을 루프가 대체.
            self.memory.append({"role": "user", "content": tool_results})

        # MAX_STEPS까지 돌아도 안 끝났다 → 강제 종료(가드 탈출).
        return "[max_steps 도달 — 루프를 강제 종료했어요]"
