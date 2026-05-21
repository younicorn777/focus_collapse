import time

from state_controller import StateController


def format_seconds(seconds):
    seconds = int(seconds)
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def print_status(controller):
    status = controller.get_status()

    print()
    print("================================")
    print("현재 상태:", status["state"])
    print("현재 작업 번호:", status["work_id"])
    print("현재 작업 시간:", format_seconds(status["current_work_seconds"]))
    print("휴식 남은 시간:", format_seconds(status["rest_left_seconds"]))
    print("점수:", status["score"])
    print("이유:", status["reason"])
    print("================================")
    print()


def main():
    # 테스트에서는 휴식 시간을 짧게 10초로 설정
    controller = StateController(rest_seconds=10)

    print("StateController 테스트")
    print("y: 노란 버튼")
    print("r: 빨간 버튼")
    print("c: AI COLLAPSED 수신")
    print("d: AI DISTRACTED 수신")
    print("f: AI FOCUSED 수신")
    print("q: 종료")
    print()
    print("테스트 기준:")
    print("- y는 새 작업 시작 / 현재 작업 종료")
    print("- r은 현재 작업 안에서 휴식 / 휴식 후 같은 작업 복귀")
    print("- 새 작업은 STOPPED 상태에서 y를 눌렀을 때만 시작")
    print()

    while True:
        event = controller.update_timer()

        if event == "rest_end":
            print("[EVENT] 휴식 종료 → REST_END_ALERT")
            print("빨간 버튼 r을 누르면 같은 작업으로 복귀합니다.")

        print_status(controller)

        command = input("입력(y/r/c/d/f/q): ").strip().lower()

        if command == "y":
            event = controller.press_yellow()
            print("[YELLOW]", event)

        elif command == "r":
            event = controller.press_red()
            print("[RED]", event)

        elif command == "c":
            event = controller.update_from_ai(
                ai_state="COLLAPSED",
                score=75,
                reason="eye_closed_or_yawn",
            )
            print("[AI COLLAPSED]", event)

        elif command == "d":
            event = controller.update_from_ai(
                ai_state="DISTRACTED",
                score=45,
                reason="yawn",
            )
            print("[AI DISTRACTED]", event)

        elif command == "f":
            event = controller.update_from_ai(
                ai_state="FOCUSED",
                score=10,
                reason="normal",
            )
            print("[AI FOCUSED]", event)

        elif command == "q":
            print("테스트 종료")
            break

        else:
            print("알 수 없는 입력입니다.")

        time.sleep(0.5)


if __name__ == "__main__":
    main()