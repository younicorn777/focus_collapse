import time
import math


MOUTH = {
    "left": 61,
    "right": 291,
    "top": 13,
    "bottom": 14,
}


class YawnDetector:
    """
    하품 감지 클래스.

    역할:
    - 입의 세로/가로 비율 계산
    - ratio가 threshold보다 크면 입 벌림으로 판단
    - 입 벌림이 open_seconds 이상 지속되면 yawn_event=True 반환
    - 한 번의 하품에 event는 1회만 발생
    - 입을 닫으면 다시 다음 하품 감지 가능
    """

    def __init__(self, threshold=0.35, open_seconds=2.0):
        self.threshold = threshold
        self.open_seconds = open_seconds

        self.open_start_time = None
        self.event_triggered = False

    def _distance(self, p1, p2):
        return math.sqrt(
            (p1.x - p2.x) ** 2
            + (p1.y - p2.y) ** 2
        )

    def _mouth_ratio(self, landmarks):
        left = landmarks[MOUTH["left"]]
        right = landmarks[MOUTH["right"]]
        top = landmarks[MOUTH["top"]]
        bottom = landmarks[MOUTH["bottom"]]

        horizontal = self._distance(left, right)
        vertical = self._distance(top, bottom)

        if horizontal == 0:
            return 0.0

        return vertical / horizontal

    def update(self, landmarks):
        current_time = time.time()

        mouth_ratio = self._mouth_ratio(landmarks)
        is_open = mouth_ratio > self.threshold

        duration = 0.0
        event = False

        if is_open:
            if self.open_start_time is None:
                self.open_start_time = current_time

            duration = current_time - self.open_start_time

            if duration >= self.open_seconds and not self.event_triggered:
                event = True
                self.event_triggered = True

        else:
            self.open_start_time = None
            self.event_triggered = False

        return {
            "is_open": is_open,
            "event": event,
            "duration": duration,
            "ratio": mouth_ratio,
        }

    def reset(self):
        self.open_start_time = None
        self.event_triggered = False