# eval.py  (clone-project 루트에서: uv run python eval.py)
"""아주 작은 eval — 정해둔 질문에 Hermes가 '기대대로' 동작하는지 자동 채점한다.
기대 동작: (1) 옳은 도구를 불렀나(= trace를 읽어 확인) + (2) 답에 정답 문자열이 들어갔나.
★ 질문은 전부 읽기 전용(search_docs)이라 승인 게이트를 건드리지 않아 비대화형으로 안전하다."""
import json
import os
import sys
from hermes.agent import Hermes
from hermes.config import LOG_FILE

# (질문, 반드시 불러야 할 도구, 최종 답에 있어야 할 문자열) — 전부 kb/의 Nimbus 문서 근거
EVAL_CASES = [
    ("Nimbus에서 동시에 배포하는 서버 수 기본값이 몇이야?", "search_docs", "4"),
    ("Nimbus로 프로덕션 배포하는 명령이 뭐야?",              "search_docs", "nimbus ship"),
]


def check(question, want_tool, want_substring):
    """한 케이스를 채점한다. trace를 비워 이 실행만 격리 → run → trace로 도구 확인 + 답 문자열 확인."""
    os.makedirs(os.path.dirname(LOG_FILE) or ".", exist_ok=True)  # 데모 전에 eval을 돌려도 logs/가 없어 안 터지게
    open(LOG_FILE, "w").close()                              # 이 케이스의 trace만 남게 비운다
    answer = Hermes().run(question)                          # fresh 메모리로 실행
    events = [json.loads(line) for line in open(LOG_FILE, encoding="utf-8")]
    tools_used = {e["tool"] for e in events}                # 이번 실행이 부른 도구들(← trace가 증거)
    tool_ok = want_tool in tools_used
    ans_ok = want_substring in answer
    passed = tool_ok and ans_ok
    print(f"[{'PASS' if passed else 'FAIL'}] {question}")
    print(f"    {want_tool} 호출? {tool_ok} · 답에 '{want_substring}' 포함? {ans_ok}")
    return passed


def main():
    results = [check(q, t, s) for q, t, s in EVAL_CASES]
    passed = sum(results)
    print(f"\n{passed}/{len(results)} 통과")
    sys.exit(0 if passed == len(results) else 1)             # CI처럼 exit code로 성패


if __name__ == "__main__":
    main()
