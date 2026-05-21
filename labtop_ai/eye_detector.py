import time
import math


LEFT_EYE = {
    "left": 33,
    "right": 133,
    "top": 159,
    "bottom": 145,
}

RIGHT_EYE = {
    "left": 362,
    "right": 263,
    "top": 386,
    "bottom": 374,
}


class EyeDetector:
    def __init__(self, threshold=0.20, closed_seconds=1.5):
        self.threshold = threshold
        self.closed_seconds = closed_seconds
        self.closed_start_time = None

    def _distance(self, p1, p2):
        return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

    def _eye_ratio(self, landmarks, eye):
        left = landmarks[eye["left"]]
        right = landmarks[eye["right"]]
        top = landmarks[eye["top"]]
        bottom = landmarks[eye["bottom"]]

        horizontal = self._distance(left, right)
        vertical = self._distance(top, bottom)

        if horizontal == 0:
            return 0

        return vertical / horizontal

    def update(self, landmarks):
        current_time = time.time()

        left_ratio = self._eye_ratio(landmarks, LEFT_EYE)
        right_ratio = self._eye_ratio(landmarks, RIGHT_EYE)
        eye_ratio = (left_ratio + right_ratio) / 2

        is_closed = eye_ratio < self.threshold
        duration = 0.0
        eye_risk = False

        if is_closed:
            if self.closed_start_time is None:
                self.closed_start_time = current_time

            duration = current_time - self.closed_start_time

            if duration >= self.closed_seconds:
                eye_risk = True
        else:
            self.closed_start_time = None

        return {
            "is_closed": is_closed,
            "risk": eye_risk,
            "duration": duration,
            "ratio": eye_ratio,
        }

    def reset(self):
        self.closed_start_time = None