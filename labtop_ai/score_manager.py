import time


class ScoreManager:
    """
    Focus Collapse Score 계산 클래스.

    역할:
    - 눈 감김 위험 상태가 지속되면 일정 간격으로 점수 증가
    - 하품 이벤트 발생 시 점수 증가
    - 정상 상태가 유지되면 일정 간격으로 점수 감소
    """

    def __init__(
        self,
        min_score=0,
        max_score=100,
        eye_risk_score=10,
        yawn_score=30,
        recovery_score=10,
        eye_risk_interval=3.0,
        recovery_seconds=10.0,
    ):
        self.min_score = min_score
        self.max_score = max_score

        self.eye_risk_score = eye_risk_score
        self.yawn_score = yawn_score
        self.recovery_score = recovery_score

        self.eye_risk_interval = eye_risk_interval
        self.recovery_seconds = recovery_seconds

        self.score = 0

        self.last_eye_score_time = 0
        self.last_recovery_time = time.time()

    def _clamp(self):
        self.score = max(self.min_score, min(self.score, self.max_score))

    def update(self, eye_risk=False, yawn_event=False, normal=False):
        """
        점수 업데이트.

        주의:
        - 하품 중 눈 감김 무시는 camera_main.py에서 처리한다.
        - COLLAPSED 이후 점수 고정은 FocusSession/camera_main.py에서 처리한다.
        """
        current_time = time.time()
        reason = "normal"

        if yawn_event:
            self.score += self.yawn_score
            self.last_recovery_time = current_time
            reason = "yawn"

        elif eye_risk:
            if current_time - self.last_eye_score_time >= self.eye_risk_interval:
                self.score += self.eye_risk_score
                self.last_eye_score_time = current_time
                reason = "eye_closed"

            self.last_recovery_time = current_time

        elif normal:
            if current_time - self.last_recovery_time >= self.recovery_seconds:
                self.score -= self.recovery_score
                self.last_recovery_time = current_time
                reason = "normal_recovery"

        else:
            self.last_recovery_time = current_time

        self._clamp()

        return {
            "score": self.score,
            "reason": reason,
        }

    def reset(self):
        """
        새 작업 시작 또는 휴식 후 복귀 시 점수 초기화.
        """
        self.score = 0
        self.last_eye_score_time = 0
        self.last_recovery_time = time.time()