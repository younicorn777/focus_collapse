import time


class ScoreManager:
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
        current_time = time.time()
        reason = "normal"

        if eye_risk and current_time - self.last_eye_score_time >= self.eye_risk_interval:
            self.score += self.eye_risk_score
            self.last_eye_score_time = current_time
            reason = "eye_closed"

        if yawn_event:
            self.score += self.yawn_score
            reason = "yawn" if reason == "normal" else reason + "+yawn"

        if normal and not eye_risk and not yawn_event:
            if current_time - self.last_recovery_time >= self.recovery_seconds:
                self.score -= self.recovery_score
                self.last_recovery_time = current_time
                reason = "normal_recovery"

        self._clamp()

        return {
            "score": self.score,
            "reason": reason,
        }

    def reset(self):
        self.score = 0
        self.last_eye_score_time = 0
        self.last_recovery_time = time.time()