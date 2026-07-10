# hermes/config.py
MODEL = "claude-sonnet-4-6"   # 모델 ID는 여기 한 곳에서만 바꾼다
MAX_TOKENS = 1024
MAX_STEPS = 8                 # agent loop 무한 반복 가드 (M3) — 도구를 최대 8스텝까지
