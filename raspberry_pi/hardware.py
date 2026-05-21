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


class HardwareController:
    """
    현재는 Mock RGB LED만 사용.
    나중에 실제 라즈베리파이 GPIO 제어 코드로 교체 가능.
    """

    def __init__(self):
        self.rgb_led = RGBLedMock()

    def update_led_by_state(self, state):
        if state == "STOPPED":
            self.rgb_led.off()

        elif state == "FOCUSED":
            self.rgb_led.green()

        elif state == "DISTRACTED":
            self.rgb_led.yellow()

        elif state == "COLLAPSED":
            self.rgb_led.blink_red()

        elif state == "RESTING":
            self.rgb_led.blue()

        elif state == "REST_END_ALERT":
            self.rgb_led.blink_blue()

        elif state == "INVALID":
            self.rgb_led.off()

        else:
            self.rgb_led.off()