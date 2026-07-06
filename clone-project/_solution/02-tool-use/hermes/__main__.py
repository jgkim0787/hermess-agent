# hermes/__main__.py
from .llm import chat_with_tools

def main():
    print("Hermes REPL — 빈 입력 또는 'exit'로 종료 (이제 도구를 쓸 수 있다)\n")
    messages = []                          # append-only 대화 history (이게 곧 '기억')
    while True:
        user = input("you> ").strip()
        if user == "" or user == "exit":   # 종료 조건
            print("bye.")
            break
        messages.append({"role": "user", "content": user})   # user 턴만 여기서 append
        answer = chat_with_tools(messages)  # 도구 왕복 + assistant append 는 이 안에서 처리
        print("hermes>", answer)

if __name__ == "__main__":
    main()
