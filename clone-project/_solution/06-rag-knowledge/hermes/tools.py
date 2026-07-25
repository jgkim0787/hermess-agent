# hermes/tools.py
"""Hermes의 도구 — 모델이 '이 입력으로 불러 달라'고 요청하면 우리가 실행한다."""
import subprocess

from . import rag   # M6 — search_docs가 부르는 RAG backend(로컬 문서 TF-IDF 검색)


# 모델에게 알려줄 도구 목록. 각 원소 = {name, description, input_schema}.
# input_schema 는 JSON Schema — 모델은 이걸 보고 인자를 어떤 모양으로 채울지 정한다.
TOOLS = [
    {
        "name": "read_file",
        "description": "지정한 경로의 텍스트 파일을 읽어 그 내용을 반환한다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "읽을 파일의 경로"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "지정한 경로에 텍스트를 파일로 쓴다(있으면 덮어쓴다).",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "쓸 파일의 경로"},
                "content": {"type": "string", "description": "파일에 쓸 내용"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "run_bash",
        "description": "셸 명령을 실행하고 표준출력을 반환한다. 파일 목록 조회 등에 쓴다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cmd": {"type": "string", "description": "실행할 셸 명령, 예: ls *.py"},
            },
            "required": ["cmd"],
        },
    },
    # M5 — update_plan: '계획'을 기록하는 도구. 여긴 스키마(모델과의 계약)만 둔다.
    # 실제 핸들러는 agent.py에 있다(아래 run_tool 주석 참고).
    {
        "name": "update_plan",
        "description": "현재 작업 계획(단계 목록)을 기록/갱신한다. 여러 단계가 필요한 목표를 받으면 "
                       "가장 먼저 이 도구로 계획을 세우고 시작한다. 계획이 바뀌면 다시 호출한다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "steps": {
                    "type": "array",                      # ← M5 신규: 지금까지의 도구는 전부 string 인자였다
                    "items": {"type": "string"},
                    "description": "실행할 단계들. 각 항목은 한 줄짜리 행동, 예: 'README.md를 읽는다'",
                },
            },
            "required": ["steps"],
        },
    },
    # M6 — search_docs: 로컬 지식 기반(kb/)을 검색하는 도구. read_file과 같은 부류의
    # '바깥 지식 조회' 도구라 스키마·구현·디스패치가 전부 tools.py에 산다(update_plan과 정반대).
    {
        "name": "search_docs",
        "description": "로컬 지식 기반(kb/) 문서를 검색해 질문과 가장 관련된 문단들을 반환한다. "
                       "사내 규칙·프로젝트 문서 등 '학습으로는 알 수 없는' 사실을 물으면 이 도구로 먼저 찾는다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "찾고 싶은 내용(자연어 질문/키워드)"},
            },
            "required": ["query"],
        },
    },
]


def read_file(path: str) -> str:
    """실제 디스크 파일을 읽어 문자열로 반환한다 (Hermes의 첫 '진짜' 도구)."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read(4000)   # 너무 큰 파일은 앞부분만 — context/토큰 절약


def write_file(path: str, content: str) -> str:
    """content를 path에 쓰고, 짧은 확인 문자열을 반환한다."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"{len(content)} bytes를 {path}에 저장했다."


def run_bash(cmd: str) -> str:
    """셸 명령을 실행하고 stdout(+stderr)을 문자열로 반환한다.

    ⚠️ 위험 — 학습용. 모델이 요청한 임의의 셸 명령을 '검증 없이 그대로' 실행한다.
    rm 같은 파괴적 명령도 그대로 돌아가므로 실제 서비스에선 절대 금물이다.

    M5(약속 회수): 이 함수는 '여전히' 검증 없이 실행한다 — 대신 agent.py의 승인 게이트가
    호출 '직전'에 사람에게 y/n을 묻는다(config.DANGEROUS_TOOLS). 도구는 '능력'만 갖고,
    무엇을 실행할지의 '정책'은 agent loop가 쥔다. 승인하면 위험은 그대로이니
    신뢰할 수 있는 로컬 학습 환경에서만 쓴다.
    """
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return (result.stdout + result.stderr) or "(출력 없음)"   # 빈 문자열이면 400 → 대체 문구


def search_docs(query: str) -> str:
    """kb/ 문서를 검색해 관련 chunk들을 '하나의 문자열'로 join해 돌려준다(M6).
    ★ rag.search는 list[str]을 준다 — 리스트를 그대로 반환하면 tool_result content가
      문자열이 아니라서 다음 create가 400이다(M2/M3 규칙). 그래서 반드시 join하고,
      결과가 없으면 빈 문자열 대신 '(관련 문서 없음)'을 돌려준다(빈 문자열도 400)."""
    hits = rag.search(query)
    return "\n\n---\n\n".join(hits) or "(관련 문서 없음)"


def run_tool(name: str, tool_input: dict) -> str:
    """도구 이름으로 실제 함수를 부르는 디스패처.
    반환은 반드시 문자열 — 그대로 tool_result 의 content 로 들어간다."""
    # update_plan은 여기(run_tool)가 아니라 agent.py가 처리한다 —
    # 바깥 세상이 아니라 '에이전트 자신의 상태(self.plan)'를 바꾸는 도구이기 때문이다(M5 설계).
    if name == "read_file":
        return read_file(tool_input["path"])
    if name == "write_file":
        return write_file(tool_input["path"], tool_input["content"])
    if name == "run_bash":
        return run_bash(tool_input["cmd"])
    if name == "search_docs":                     # M6 — '바깥 지식 조회' 도구라 여기 넣는다
        return search_docs(tool_input["query"])
    return f"[unknown tool: {name}]"
