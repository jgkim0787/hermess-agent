# hermes/config.py
MODEL = "claude-sonnet-4-6"   # 모델 ID는 여기 한 곳에서만 바꾼다
MAX_TOKENS = 1024
MAX_STEPS = 8                 # agent loop 무한 반복 가드 (M3) — 도구를 최대 8스텝까지

# M4 — Memory & Context: compaction(대화 요약 압축)용 상수
# COMPACT_THRESHOLD는 학습용으로 일부러 낮췄다 — 실제 claude-sonnet-4-6의
# context window는 1M tokens라 이 정도로는 안 터진다. 낮춰야 압축이 눈에 보인다.
COMPACT_THRESHOLD = 4000      # token_estimate가 이 값을 넘으면 compaction 발동
KEEP_RECENT = 6               # compaction 시 보존할 최근 메시지 수(그 이전을 요약 1개로)
