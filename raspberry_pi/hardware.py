import time


class RGBLedMock:
    """
    노트북 테스트용 Mock RGB LED 클래스.
    실제 라즈베리파이 GPIO 없이도 상태별 LED 동작을 터미널에서 확인할 수 있다.
    """

    def __init__(self):
        self.current_color = "OFF"

    def off(self):
        self.current_color = "OFF"
        print("[RGB LED] OFF")

    def green(self):
        self.current_color = "GREEN"
        print("[RGB LED] GREEN - FOCUSED")

    def yellow(self):
        self.current_color = "YELLOW"
        print("[RGB LED] YELLOW - DISTRACTED")

    def red(self):
        self.current_color = "RED"
        print("[RGB LED] RED - COLLAPSED")

    def blue(self):
        self.current_color = "BLUE"
        print("[RGB LED] BLUE - RESTING")

    def blink_red(self, times=3, interval=0.3):
        print("[RGB LED] RED BLINK - COLLAPSED")
        for _ in range(times):
            self.red()
            time.sleep(interval)
            self.off()
            time.sleep(interval)

    def blink_blue(self, times=3, interval=0.3):
        print("[RGB LED] BLUE BLINK - REST END ALERT")
        for _ in range(times):
            self.blue()
            time.sleep(interval)
            self.off()
            time.sleep(interval)


class ActiveBuzzerMock:
    """
    노트북 테스트용 Mock 능동 부저 클래스.
    실제 GPIO 대신 터미널 출력으로 부저 동작을 확인한다.
    """

    def __init__(self):
        self.is_on = False

    def on(self):
        self.is_on = True
        print("[BUZZER] ON")

    def off(self):
        self.is_on = False
        print("[BUZZER] OFF")

    def warning_beep(self, times=3, interval=0.25):
        print("[BUZZER] WARNING BEEP - COLLAPSED")
        for _ in range(times):
            self.on()
            time.sleep(interval)
            self.off()
            time.sleep(interval)

    def short_beep(self, times=2, interval=0.15):
        print("[BUZZER] SHORT BEEP - REST END ALERT")
        for _ in range(times):
            self.on()
            time.sleep(interval)
            self.off()
            time.sleep(interval)


class HardwareController:
    """
    현재는 Mock RGB LED + Mock 능동 부저 사용.
    나중에 실제 라즈베리파이 GPIO 제어 코드로 교체 가능.
    """

    def __init__(self):
        self.rgb_led = RGBLedMock()
        self.buzzer = ActiveBuzzerMock()

    def update_by_state(self, state):
        """
        상태에 따라 RGB LED와 부저를 함께 제어한다.
        """

        if state == "STOPPED":
            self.rgb_led.off()
            self.buzzer.off()

        elif state == "FOCUSED":
            self.rgb_led.green()
            self.buzzer.off()

        elif state == "DISTRACTED":
            self.rgb_led.yellow()
            self.buzzer.off()

        elif state == "COLLAPSED":
            self.rgb_led.blink_red()
            self.buzzer.warning_beep()

        elif state == "RESTING":
            self.rgb_led.blue()
            self.buzzer.off()

        elif state == "REST_END_ALERT":
            self.rgb_led.blink_blue()
            self.buzzer.short_beep()

        elif state == "INVALID":
            self.rgb_led.off()
            self.buzzer.off()

        else:
            self.rgb_led.off()
            self.buzzer.off()

    def buzzer_off(self):
        """
        빨간 버튼으로 경고를 확인했을 때 부저를 끄기 위한 함수.
        """
        self.buzzer.off()