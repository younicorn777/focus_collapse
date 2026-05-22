import time
from datetime import datetime

from session_storage import SessionStorage


class FocusSession:
    """
    노트북 측 작업/휴식 상태 관리 클래스.

    노트북이 전체 상태를 관리하고,
    라즈베리파이는 이 클래스가 만든 payload를 받아 출력만 수행한다.
    """

    WORK_STATES = ["FOCUSED", "DISTRACTED", "COLLAPSED", "INVALID"]

    def __init__(self, rest_seconds=20):
        self.storage = SessionStorage()

        self.state = "STOPPED"

        self.work_id = self.storage.get_last_work_id()

        self.work_seconds = 0
        self.work_start_time = None

        self.rest_seconds = rest_seconds
        self.rest_start_time = None

        self.score = 0
        self.reason = "ready"

        self.collapsed_locked = False

    # ============================================================
    # Time
    # ============================================================

    def get_current_work_seconds(self):
        if self.state in self.WORK_STATES:
            if self.work_start_time is not None:
                return self.work_seconds + (time.time() - self.work_start_time)

        return self.work_seconds

    def get_rest_left_seconds(self):
        if self.state != "RESTING" or self.rest_start_time is None:
            return 0

        elapsed = time.time() - self.rest_start_time
        left = self.rest_seconds - elapsed

        return max(0, left)

    def get_timestamp(self):
        return datetime.now().strftime("%H:%M:%S")

    # ============================================================
    # Reset
    # ============================================================

    def reset_score(self):
        self.score = 0
        self.reason = "score_reset"
        self.collapsed_locked = False

    # ============================================================
    # Keyboard Events
    # ============================================================

    def start_work(self):
        """
        s 키:
        새 작업 시작.
        work_id 증가, 작업 시간 0초, score 0.
        """
        if self.state != "STOPPED":
            return "ignored"

        self.work_id += 1
        self.storage.update_last_work_id(self.work_id)

        self.work_seconds = 0
        self.work_start_time = time.time()

        self.rest_start_time = None

        self.score = 0
        self.reason = "start_work"
        self.collapsed_locked = False

        self.state = "FOCUSED"

        return "start_work"

    def stop_work(self):
        """
        x 키:
        작업 종료.
        어떤 상태에서든 STOPPED로 전환 가능.
        """
        if self.state == "STOPPED":
            return "ignored"

        if self.work_start_time is not None:
            self.work_seconds = self.get_current_work_seconds()

        self.work_start_time = None
        self.rest_start_time = None

        self.state = "STOPPED"
        self.reason = "stop_work"
        self.collapsed_locked = False

        return "stop_work"

    def start_rest(self):
        """
        r 키:
        작업 중 또는 COLLAPSED 상태에서 휴식 시작.
        """
        if self.state not in self.WORK_STATES:
            return "ignored"

        self.work_seconds = self.get_current_work_seconds()
        self.work_start_time = None

        self.rest_start_time = time.time()

        if self.state == "COLLAPSED":
            self.reason = "collapse_rest"
        else:
            self.reason = "manual_rest"

        self.state = "RESTING"
        self.collapsed_locked = False

        return "rest_start"

    def end_rest(self):
        """
        e 키:
        REST_END_ALERT 상태에서 같은 작업으로 복귀.
        score는 0으로 초기화.
        """
        if self.state != "REST_END_ALERT":
            return "ignored"

        self.rest_start_time = None
        self.work_start_time = time.time()

        self.score = 0
        self.reason = "resume_work"
        self.collapsed_locked = False

        self.state = "FOCUSED"

        return "resume_work"

    # ============================================================
    # Timer
    # ============================================================

    def update_timer(self):
        """
        RESTING 상태에서 휴식 시간이 끝나면 REST_END_ALERT로 전환.
        e 키를 누르기 전까지 REST_END_ALERT 유지.
        """
        if self.state == "RESTING":
            if self.get_rest_left_seconds() <= 0:
                self.rest_start_time = None
                self.state = "REST_END_ALERT"
                self.reason = "rest_finished"
                return "rest_end"

        return "none"

    # ============================================================
    # AI State Update
    # ============================================================

    def update_ai_state(self, score, reason="normal"):
        """
        AI 점수 결과를 상태에 반영.

        적용 조건:
        - 작업 중 상태에서만 반영
        - RESTING / REST_END_ALERT / STOPPED에서는 무시
        - COLLAPSED가 된 뒤에는 r 또는 x 전까지 고정
        """
        if self.state not in self.WORK_STATES:
            return "none"

        if self.collapsed_locked:
            return "none"

        self.score = score
        self.reason = reason

        previous_state = self.state

        if previous_state == "INVALID":
            self.reason = "face_recovered"

        if self.score >= 60:
            self.state = "COLLAPSED"
            self.collapsed_locked = True
            return "collapse"

        if self.score >= 30:
            self.state = "DISTRACTED"
        else:
            self.state = "FOCUSED"

        if self.state != previous_state:
            return "state_change"

        return "none"

    # ============================================================
    # Payload
    # ============================================================

    def make_payload(self, event="heartbeat"):
        """
        라즈베리파이로 전송할 데이터 생성.
        """
        return {
            "state": self.state,
            "score": int(self.score),
            "reason": self.reason,
            "event": event,
            "work_id": self.work_id,
            "work_seconds": int(self.get_current_work_seconds()),
            "rest_left_seconds": int(self.get_rest_left_seconds()),
            "timestamp": self.get_timestamp(),
        }