# hermes/__main__.py
from .llm import stream_chat

def main():
    print("Hermes REPL — 빈 입력 또는 'exit'로 종료\n")
    messages = []                          # append-only 대화 history (이게 곧 '기억')
    while True:
        user = input("you> ").strip()
        if user == "" or user == "exit":   # 종료 조건
            print("bye.")
            break
        messages.append({"role": "user", "content": user})
        print("hermes> ", end="", flush=True)
        answer = stream_chat(messages)     # 전체 history를 보내고 token을 흘려 출력
        messages.append({"role": "assistant", "content": answer})  # 답도 history에 누적

if __name__ == "__main__":
    main()
