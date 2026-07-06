# hermes/tools.py
"""Hermes의 도구 — 모델이 '이 입력으로 불러 달라'고 요청하면 우리가 실행한다."""


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
]


def read_file(path: str) -> str:
    """실제 디스크 파일을 읽어 문자열로 반환한다 (Hermes의 첫 '진짜' 도구)."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read(4000)   # 너무 큰 파일은 앞부분만 — context/토큰 절약


def run_tool(name: str, tool_input: dict) -> str:
    """도구 이름으로 실제 함수를 부르는 디스패처.
    반환은 반드시 문자열 — 그대로 tool_result 의 content 로 들어간다."""
    if name == "read_file":
        return read_file(tool_input["path"])
    return f"[unknown tool: {name}]"
