class LCDMock:
    """
    노트북 테스트용 Mock LCD 클래스.
    실제 LCD 대신 터미널에 LCD 출력 내용을 보여준다.
    """

    def __init__(self):
        self.last_line1 = ""
        self.last_line2 = ""

    def clear(self):
        self.last_line1 = ""
        self.last_line2 = ""
        print("[LCD] CLEAR")

    def display(self, line1, line2=""):
        """
        LCD 2줄 출력.
        같은 내용이 반복 출력되지 않도록 이전 출력과 비교한다.
        """
        line1 = str(line1)[:16]
        line2 = str(line2)[:16]

        if line1 == self.last_line1 and line2 == self.last_line2:
            return

        self.last_line1 = line1
        self.last_line2 = line2

        print("[LCD]")
        print(f" {line1}")
        print(f" {line2}")


class LCDController:
    """
    상태 정보에 따라 LCD에 표시할 문구를 결정한다.
    """

    def __init__(self):
        self.lcd = LCDMock()

    def format_seconds(self, seconds):
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def update_by_status(self, status):
        state = status["state"]
        work_time = self.format_seconds(status["current_work_seconds"])
        rest_left = self.format_seconds(status["rest_left_seconds"])

        if state == "STOPPED":
            self.lcd.display("Focus AI Ready", "Press YELLOW")

        elif state == "FOCUSED":
            self.lcd.display("FOCUSED", f"Work: {work_time}")

        elif state == "DISTRACTED":
            self.lcd.display("DISTRACTED", f"Work: {work_time}")

        elif state == "COLLAPSED":
            self.lcd.display("FOCUS WARNING", f"Work: {work_time}")

        elif state == "RESTING":
            self.lcd.display("RESTING", f"Left: {rest_left}")

        elif state == "REST_END_ALERT":
            self.lcd.display("BREAK FINISHED", "Press RED")

        elif state == "INVALID":
            self.lcd.display("FACE NOT FOUND", "Check Camera")

        else:
            self.lcd.display("UNKNOWN", state)