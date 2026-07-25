# hermes/__main__.py
from .agent import Hermes

def main():
    print("Hermes REPL — 빈 입력 또는 'exit'로 종료 (이제 도구를 여러 스텝 이어 쓴다)\n")
    hermes = Hermes()                      # history 소유권이 Hermes로 이동 (self.messages)
    while True:
        user = input("you> ").strip()
        if user == "" or user == "exit":   # 종료 조건
            print("bye.")
            break
        answer = hermes.run(user)          # agent loop(while)는 이 안에서. user append 도 run이 처리
        print("hermes>", answer)

if __name__ == "__main__":
    main()
