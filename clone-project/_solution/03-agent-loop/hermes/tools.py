# hermes/tools.py
"""Hermes의 도구 — 모델이 '이 입력으로 불러 달라'고 요청하면 우리가 실행한다."""
import subprocess


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
    실행 전 사용자 승인(승인 게이트)은 M5에서 추가한다. 지금은 신뢰할 수 있는
    로컬 학습 환경에서만 쓴다.
    """
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return (result.stdout + result.stderr) or "(출력 없음)"   # 빈 문자열이면 400 → 대체 문구


def run_tool(name: str, tool_input: dict) -> str:
    """도구 이름으로 실제 함수를 부르는 디스패처.
    반환은 반드시 문자열 — 그대로 tool_result 의 content 로 들어간다."""
    if name == "read_file":
        return read_file(tool_input["path"])
    if name == "write_file":
        return write_file(tool_input["path"], tool_input["content"])
    if name == "run_bash":
        return run_bash(tool_input["cmd"])
    return f"[unknown tool: {name}]"
