# hermes/memory.py
"""Hermes의 대화 메모리 — 누적된 history를 소유하고, 너무 길어지면 스스로 압축한다.

M3까지 agent.py가 직접 들던 self.messages(평범한 list)를 이 class Memory로 승격한다.
list처럼 .append로 쌓되, API로 넘기기 직전(to_messages)에 토큰을 추정해 임계를 넘으면
오래된 메시지들을 '요약 1개'로 접는다(compaction). append 사용감은 list 그대로라
agent.py 변경은 최소가 된다."""
from .llm import client                      # 요약도 같은 Claude 클라이언트로 (재사용)
from .config import MODEL, COMPACT_THRESHOLD, KEEP_RECENT


class Memory:
    def __init__(self, threshold=COMPACT_THRESHOLD, keep_recent=KEEP_RECENT):
        self.messages = []              # append-only 로그 — M3의 self.messages가 이 안으로 들어왔다
        self.threshold = threshold      # 이 추정 토큰 수를 넘으면 compaction
        self.keep_recent = keep_recent  # 압축해도 최근 이만큼은 원문 그대로 보존

    def append(self, msg):
        """list.append과 똑같은 사용감 — agent.py는 self.memory.append처럼 쓴다."""
        self.messages.append(msg)

    def token_estimate(self) -> int:
        """정확한 토크나이저(count_tokens, 네트워크 왕복) 대신 문자 수 // 4로 근사.
        가드(임계 판단)에는 이 싼 추정으로 충분하다."""
        return sum(len(_text_of(m)) for m in self.messages) // 4

    def to_messages(self) -> list:
        """API 전송용 history를 반환한다. ★ 여기서 압축이 자동 발동한다:
        추정 토큰이 임계를 넘으면 compact()로 오래된 대화를 접은 뒤 반환한다.
        agent loop는 이 사실을 몰라도 된다(캡슐화)."""
        if self.token_estimate() > self.threshold:
            self.compact()
        return self.messages

    def compact(self):
        """최근 keep_recent개는 원문 보존, 그 이전 오래된 메시지들을 요약 1개로 대체한다."""
        cut = len(self.messages) - self.keep_recent
        if cut <= 0:
            return
        # ★ 경계 가드: 보존 구간이 tool_result로 시작하면 그 짝 tool_use가 요약에 먹혀
        # 다음 호출이 400(orphan tool_result)이 난다. 경계를 앞으로 물려 쌍을 안 쪼갠다.
        while cut > 0 and _is_tool_result_turn(self.messages[cut]):
            cut -= 1
        if cut <= 0:
            return
        old, recent = self.messages[:cut], self.messages[cut:]
        summary = self._summarize(old)
        # 요약은 '첫 user 메시지'로 prepend — history는 늘 user로 시작해야 하니 안전하다.
        self.messages = [{"role": "user", "content": f"[이전 대화 요약]\n{summary}"}] + recent
        print(f"  [memory] compaction: {len(old) + len(recent)} msgs → {len(recent) + 1} msgs")

    def _summarize(self, old) -> str:
        """오래된 메시지들을 별도 LLM 호출로 요약한다.
        tools 없음, Hermes persona(SYSTEM)도 아님 — 요약 전용 system을 따로 준다."""
        log = "\n".join(f"{m['role']}: {_text_of(m)}" for m in old)
        resp = client.messages.create(
            model=MODEL,
            max_tokens=512,
            system="다음 대화 로그를 이후 대화에 필요한 사실 위주로 3~5문장으로 간결히 요약해줘.",
            messages=[{"role": "user", "content": log}],
        )
        return "".join(b.text for b in resp.content if b.type == "text")


def _text_of(msg) -> str:
    """content를 문자열로 — 블록 리스트/dict여도 str()로 안전 직렬화(추정·요약용)."""
    c = msg["content"]
    return c if isinstance(c, str) else str(c)


def _is_tool_result_turn(msg) -> bool:
    """이 메시지가 tool_result 턴인가(경계 가드용).
    content가 블록 리스트이고 그 안에 type == 'tool_result' 블록이 있으면 True.
    우리가 만든 dict·SDK 객체 둘 다 대응한다."""
    c = msg["content"]
    if not isinstance(c, list):
        return False
    for b in c:
        t = b.get("type") if isinstance(b, dict) else getattr(b, "type", None)
        if t == "tool_result":
            return True
    return False
