# hermes/config.py
MODEL = "claude-sonnet-4-6"   # 모델 ID는 여기 한 곳에서만 바꾼다
MAX_TOKENS = 1024
MAX_STEPS = 8                 # agent loop 무한 반복 가드 (M3) — 도구를 최대 8스텝까지

# M4 — Memory & Context: compaction(대화 요약 압축)용 상수
# COMPACT_THRESHOLD는 학습용으로 일부러 낮췄다 — 실제 claude-sonnet-4-6의
# context window는 1M tokens라 이 정도로는 안 터진다. 낮춰야 압축이 눈에 보인다.
COMPACT_THRESHOLD = 4000      # token_estimate가 이 값을 넘으면 compaction 발동
KEEP_RECENT = 6               # compaction 시 보존할 최근 메시지 수(그 이전을 요약 1개로)

# M5 — Planning & Autonomy: 승인 게이트(guardrail)를 걸 '위험 도구' 목록
# 기준은 "되돌릴 수 있는가?" — read_file은 읽기만 하니 잘못 돌아도 되돌릴 게 없다(자동 실행).
# write_file은 덮어쓰고, run_bash는 뭐든 할 수 있다(rm 포함) → 실행 전 사람에게 묻는다.
DANGEROUS_TOOLS = {"write_file", "run_bash"}   # 반드시 집합(set) — 문자열로 쓰면 in이 부분문자열 검사가 된다
