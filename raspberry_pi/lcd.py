try:
    from RPLCD.i2c import CharLCD
    LCD_AVAILABLE = True
except ImportError:
    LCD_AVAILABLE = False


LCD_I2C_ADDRESS = 0x27


class LCDController:
    """
    I2C LCD 출력 제어 클래스.

    역할:
    - 노트북에서 받은 state, work_seconds, rest_left_seconds를 LCD에 표시
    - LCD는 16x2 기준
    - 같은 문구가 반복될 경우 다시 출력하지 않아 깜빡임을 줄임
    """

    def __init__(self):
        self.last_line1 = ""
        self.last_line2 = ""

        if LCD_AVAILABLE:
            try:
                self.lcd = CharLCD(
                    i2c_expander="PCF8574",
                    address=LCD_I2C_ADDRESS,
                    port=1,
                    cols=16,
                    rows=2,
                    charmap="A00",
                    auto_linebreaks=True,
                )

                self.lcd.clear() # 너무 깜빡이면 제거해도 됨.
                print("[LCD] I2C mode")

            except Exception as e:
                self.lcd = None
                print("[LCD ERROR]", e)
                print("[LCD] Mock mode")

        else:
            self.lcd = None
            print("[LCD] Mock mode")

    def format_seconds(self, seconds):
        seconds = int(seconds)

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def display(self, line1, line2=""):
        """
        LCD 2줄 출력.
        16x2 LCD 기준으로 각 줄은 16글자까지만 표시.
        """
        line1 = str(line1)[:16]
        line2 = str(line2)[:16]

        if line1 == self.last_line1 and line2 == self.last_line2:
            return

        self.last_line1 = line1
        self.last_line2 = line2

        if self.lcd is not None:
            self.lcd.clear()
            self.lcd.write_string(line1)
            self.lcd.cursor_pos = (1, 0)
            self.lcd.write_string(line2)

        else:
            print("[LCD]")
            print(f" {line1}")
            print(f" {line2}")

    def update_by_status(self, data):
        """
        노트북에서 받은 data를 기준으로 LCD 표시.

        data 예:
        {
            "state": "FOCUSED",
            "work_seconds": 120,
            "rest_left_seconds": 0
        }
        """
        state = data.get("state", "STOPPED")
        work_seconds = data.get("work_seconds", 0)
        rest_left_seconds = data.get("rest_left_seconds", 0)

        work_time = self.format_seconds(work_seconds)
        rest_left = self.format_seconds(rest_left_seconds)

        if state == "STOPPED":
            self.display("Focus AI Ready", "Press S on PC")

        elif state == "FOCUSED":
            self.display("FOCUSED", f"Work: {work_time}")

        elif state == "DISTRACTED":
            self.display("DISTRACTED", f"Work: {work_time}")

        elif state == "COLLAPSED":
            self.display("FOCUS WARNING", f"Work: {work_time}")

        elif state == "RESTING":
            self.display("RESTING", f"Left: {rest_left}")

        elif state == "REST_END_ALERT":
            self.display("BREAK FINISHED", "Press E on PC")

        elif state == "INVALID":
            self.display("FACE NOT FOUND", "Check Camera")

        else:
            self.display("UNKNOWN", state)

    def close(self):
        if self.lcd is not None:
            self.lcd.clear()