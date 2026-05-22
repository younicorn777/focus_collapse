from gpiozero import RGBLED, Buzzer


class HardwareController:
    """
    RGB LED + 능동 부저 제어 클래스.

    역할:
    - state에 따라 LED 색상 변경
    - COLLAPSED 시 빨간 LED 점멸 + 반복 비프음
    - REST_END_ALERT 시 파란 LED 점멸 + 반복 비프음
    """

    def __init__(self):
        # ====================================================
        # GPIO PIN SETUP
        # ====================================================

        self.led = RGBLED(
            red=22,
            green=23,
            blue=24,
            active_high=True,
            initial_value=(0, 0, 0),
        )

        self.buzzer = Buzzer(25)

        self.current_state = None

        self.all_off()

        print("[HARDWARE] initialized")

    # ========================================================
    # LED CONTROL
    # ========================================================

    def led_off(self):
        self.led.off()

    def set_green(self):
        self.led.color = (0, 1, 0)

    def set_yellow(self):
        self.led.color = (1, 1, 0)

    def set_blue(self):
        self.led.color = (0, 0, 1)

    def blink_red(self):
        self.led.blink(
            on_time=0.5,
            off_time=0.5,
            on_color=(1, 0, 0),
            off_color=(0, 0, 0),
            background=True,
        )

    def blink_blue(self):
        self.led.blink(
            on_time=0.5,
            off_time=0.5,
            on_color=(0, 0, 1),
            off_color=(0, 0, 0),
            background=True,
        )

    # ========================================================
    # BUZZER CONTROL
    # ========================================================

    def buzzer_off(self):
        self.buzzer.off()

    def start_beep(self):
        """
        반복 비프음 시작.
        """
        self.buzzer.beep(
            on_time=0.3,
            off_time=0.3,
            background=True,
        )

    # ========================================================
    # STATE UPDATE
    # ========================================================

    def update_by_state(self, state):
        """
        노트북에서 받은 state 기준으로 LED/부저 상태 변경.
        """
        if state == self.current_state:
            return

        self.current_state = state

        print(f"[HARDWARE] state -> {state}")

        self.led.off()
        self.buzzer.off()

        if state == "STOPPED":
            pass

        elif state == "FOCUSED":
            self.set_green()

        elif state == "DISTRACTED":
            self.set_yellow()

        elif state == "COLLAPSED":
            self.blink_red()
            self.start_beep()

        elif state == "RESTING":
            self.set_blue()

        elif state == "REST_END_ALERT":
            self.blink_blue()
            self.start_beep()

        elif state == "INVALID":
            pass

        else:
            self.all_off()

    # ========================================================
    # ALL OFF
    # ========================================================

    def all_off(self):
        self.led.off()
        self.buzzer.off()

    # ========================================================
    # CLEANUP
    # ========================================================

    def close(self):
        self.all_off()

        try:
            self.led.close()
        except:
            pass

        try:
            self.buzzer.close()
        except:
            pass

        print("[HARDWARE] closed")