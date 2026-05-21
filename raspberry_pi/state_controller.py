import time

class StateController:
    def __init__(self, rest_seconds=20):
        self.state = "STOPPED"

        # 작업 구분 기준: 노란 버튼으로 새 작업 시작할 때 증가
        self.current_work_id = 0

        # 현재 작업의 누적 작업 시간
        # 휴식 시간은 포함하지 않음
        self.current_work_seconds = 0
        self.work_start_time = None

        # 휴식 관리
        self.rest_start_time = None
        self.rest_seconds = rest_seconds

        # 마지막 AI/버튼 정보
        self.last_reason = "ready"
        self.last_score = 0

    def get_current_work_seconds(self):
        """
        현재 작업의 누적 작업 시간 반환.
        FOCUSED / DISTRACTED / COLLAPSED 상태에서는
        현재 진행 중인 구간 시간까지 더해서 반환한다.
        """
        if self.state in ["FOCUSED", "DISTRACTED", "COLLAPSED"]:
            if self.work_start_time is not None:
                return self.current_work_seconds + (time.time() - self.work_start_time)

        return self.current_work_seconds

    def get_rest_left_seconds(self):
        """
        휴식 남은 시간 반환.
        RESTING 상태가 아니면 0 반환.
        """
        if self.state != "RESTING" or self.rest_start_time is None:
            return 0

        elapsed = time.time() - self.rest_start_time
        left = self.rest_seconds - elapsed

        return max(0, left)

    def press_yellow(self):
        """
        노란 버튼:
        - STOPPED 상태: 새 작업 시작
        - 작업 중 상태: 현재 작업 종료
        """
        if self.state == "STOPPED":
            # 새 작업 시작
            self.current_work_id += 1
            self.current_work_seconds = 0
            self.work_start_time = time.time()

            self.state = "FOCUSED"
            self.last_reason = "start_button"
            self.last_score = 0

            return "start_session"

        if self.state in ["FOCUSED", "DISTRACTED", "COLLAPSED"]:
            # 현재 작업 종료
            self.current_work_seconds = self.get_current_work_seconds()
            self.work_start_time = None

            self.state = "STOPPED"
            self.last_reason = "yellow_button"

            return "stop_session"

        # RESTING 또는 REST_END_ALERT 상태에서는 노란 버튼 무시
        return "ignored"

    def press_red(self):
        """
        빨간 버튼:
        - FOCUSED / DISTRACTED: 현재 작업 안에서 수동 휴식 시작
        - COLLAPSED: 경고 확인 후 현재 작업 안에서 휴식 시작
        - REST_END_ALERT: 같은 작업으로 복귀
        """
        if self.state in ["FOCUSED", "DISTRACTED", "COLLAPSED"]:
            previous_state = self.state

            # 휴식 시작 전까지의 현재 작업 시간 저장
            self.current_work_seconds = self.get_current_work_seconds()
            self.work_start_time = None

            self.state = "RESTING"
            self.rest_start_time = time.time()

            if previous_state == "COLLAPSED":
                self.last_reason = "collapse_confirmed"
            else:
                self.last_reason = "manual_rest"

            return "rest_start"

        if self.state == "REST_END_ALERT":
            # 같은 작업 이어서 재개
            self.state = "FOCUSED"
            self.work_start_time = time.time()
            self.rest_start_time = None
            self.last_reason = "resume_work"

            return "resume_work"

        return "ignored"

    def update_from_ai(self, ai_state, score=0, reason=""):
        """
        노트북 AI가 보낸 상태를 반영한다.
        단, 작업이 시작된 상태에서만 반영한다.
        STOPPED / RESTING / REST_END_ALERT 상태에서는 AI 상태를 무시한다.
        """
        self.last_score = score
        self.last_reason = reason

        if self.state in ["STOPPED", "RESTING", "REST_END_ALERT"]:
            return "ignored"

        if ai_state in ["FOCUSED", "DISTRACTED", "COLLAPSED", "INVALID"]:
            self.state = ai_state
            return "ai_state_update"

        return "ignored"

    def update_timer(self):
        """
        RESTING 상태에서 휴식 시간이 끝나면 REST_END_ALERT로 전환한다.
        """
        if self.state == "RESTING":
            if self.get_rest_left_seconds() <= 0:
                self.state = "REST_END_ALERT"
                self.rest_start_time = None
                self.last_reason = "rest_finished"
                return "rest_end"

        return "none"

    def get_status(self):
        """
        LCD 출력이나 테스트 출력에 사용할 현재 상태 정보.
        """
        return {
            "state": self.state,
            "work_id": self.current_work_id,
            "score": self.last_score,
            "reason": self.last_reason,
            "current_work_seconds": int(self.get_current_work_seconds()),
            "rest_left_seconds": int(self.get_rest_left_seconds()),
        }