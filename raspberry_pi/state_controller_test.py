import time

from state_controller import StateController
from hardware import HardwareController
from lcd import LCDController


def format_seconds(seconds):
    seconds = int(seconds)

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


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


def update_outputs(controller, hardware, lcd, previous_state):
    """
    상태에 따라 LED/부저/LCD 출력을 갱신한다.

    - LED/부저는 상태가 바뀔 때만 갱신
    - LCD는 작업 시간/휴식 시간이 계속 변하므로 매번 갱신
    """
    status = controller.get_status()
    current_state = status["state"]

    if current_state != previous_state:
        hardware.update_by_state(current_state)

    lcd.update_by_status(status)

    return current_state


def main():
    # 테스트용 휴식 시간: 10초
    controller = StateController(rest_seconds=10)
    hardware = HardwareController()
    lcd = LCDController()

    print("StateController + Hardware + LCD 테스트")
    print()
    print("입력 키")
    print("- y: 노란 버튼 | 새 작업 시작 / 현재 작업 종료")
    print("- r: 빨간 버튼 | 현재 작업 안에서 휴식 / 휴식 후 같은 작업 복귀")
    print("- c: AI COLLAPSED 수신")
    print("- d: AI DISTRACTED 수신")
    print("- f: AI FOCUSED 수신")
    print("- q: 종료")
    print()
    print("테스트 기준")
    print("- 새 작업은 STOPPED 상태에서 y를 눌렀을 때만 시작")
    print("- r로 휴식 후 복귀하면 같은 작업 번호를 유지")
    print("- 작업을 종료하고 다시 y를 누르면 새 작업 번호로 시작")
    print("- LCD에는 현재 작업 시간만 표시")
    print()

    last_state = None
    last_state = update_outputs(controller, hardware, lcd, last_state)

    while True:
        # 휴식 타이머 확인
        timer_event = controller.update_timer()

        if timer_event == "rest_end":
            print("[TIMER] 휴식 종료 → REST_END_ALERT")
            print("[INFO] 빨간 버튼 r을 누르면 같은 작업으로 복귀합니다.")

        last_state = update_outputs(controller, hardware, lcd, last_state)

        print_status(controller)

        command = input("입력(y/r/c/d/f/q): ").strip().lower()

        if command == "y":
            event = controller.press_yellow()
            print("[YELLOW]", event)

        elif command == "r":
            event = controller.press_red()
            print("[RED]", event)

            # 경고 확인 또는 휴식 복귀 시 부저를 꺼준다.
            hardware.buzzer_off()

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
            hardware.buzzer_off()
            break

        else:
            print("알 수 없는 입력입니다.")

        last_state = update_outputs(controller, hardware, lcd, last_state)

        time.sleep(0.5)


if __name__ == "__main__":
    main()