# hermes/trace.py
"""실행 trace 로깅 — agent loop가 부른 도구를 logs/trace.jsonl에 한 줄씩 남긴다(observability).
M6까지의 print(흘려보내고 사라짐)를 '구조화된 영속 로그'로 승격한 것. 로직은 안 바꾼다 — 관찰만 한다."""
import json
import os
import datetime
from .config import LOG_DIR, LOG_FILE


def log_event(step, tool, tool_input, result, approved=True):
    """한 번의 도구 호출을 JSON 한 줄(jsonl)로 LOG_FILE에 append한다.
    result는 앞부분만 잘라 저장한다 — trace는 '무슨 일이 있었나'의 요약이지 전체 덤프가 아니다."""
    os.makedirs(LOG_DIR, exist_ok=True)                       # logs/ 없으면 생성
    event = {
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        "step": step,
        "tool": tool,
        "input": tool_input,
        "result_preview": str(result)[:200],                  # 길면 자른다(search_docs/read_file 대비)
        "approved": approved,                                 # 거부(게이트)도 기록 — '무엇을 막았나'도 관찰
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")  # 한글 보존(ensure_ascii=False)
