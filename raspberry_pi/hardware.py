from gpiozero import RGBLED, Buzzer
from time import sleep


class HardwareController:
    """
    RGB LED + 능동 부저 제어 클래스

    역할:
    - state에 따라 LED 색상 변경
    - COLLAPSED 시 부저 울림
    - REST_END_ALERT 시 짧은 알림음
    """

    def __init__(self):
        # ====================================================
        # GPIO PIN SETUP
        # ====================================================

        # RGB LED
        self.led = RGBLED(
            red=22,
            green=23,
            blue=24,
            active_high=True,
        )

        # 능동 부저
        self.buzzer = Buzzer(25)

        # 현재 상태 저장
        self.current_state = None

        # 초기 상태
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

    def set_red(self):
        self.led.color = (1, 0, 0)

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

    def buzzer_on(self):
        self.buzzer.on()

    def buzzer_off(self):
        self.buzzer.off()

    def short_beep(self):
        """
        REST_END_ALERT 용 짧은 알림음
        """
        self.buzzer.on()
        sleep(0.2)
        self.buzzer.off()

    # ========================================================
    # STATE UPDATE
    # ========================================================

    def update_by_state(self, state):
        """
        노트북에서 받은 state 기준으로
        LED/부저 상태 변경
        """

        # 같은 상태 반복이면 불필요한 GPIO 변경 방지
        if state == self.current_state:
            return

        self.current_state = state

        print(f"[HARDWARE] state -> {state}")

        # 상태 변경 전 초기화
        self.led.off()
        self.buzzer.off()

        # ====================================================
        # STOPPED
        # ====================================================

        if state == "STOPPED":
            pass

        # ====================================================
        # FOCUSED
        # ====================================================

        elif state == "FOCUSED":
            self.set_green()

        # ====================================================
        # DISTRACTED
        # ====================================================

        elif state == "DISTRACTED":
            self.set_yellow()

        # ====================================================
        # COLLAPSED
        # ====================================================

        elif state == "COLLAPSED":
            self.blink_red()
            self.buzzer_on()

        # ====================================================
        # RESTING
        # ====================================================

        elif state == "RESTING":
            self.set_blue()

        # ====================================================
        # REST_END_ALERT
        # ====================================================

        elif state == "REST_END_ALERT":
            self.blink_blue()
            self.short_beep()

        # ====================================================
        # INVALID
        # ====================================================

        elif state == "INVALID":
            pass

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