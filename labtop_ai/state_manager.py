class StateManager:
    def __init__(self, distracted_threshold=30, collapsed_threshold=60):
        self.distracted_threshold = distracted_threshold
        self.collapsed_threshold = collapsed_threshold

    def update(self, score, abnormal_detected=False):
        if score >= self.collapsed_threshold:
            if abnormal_detected:
                return "COLLAPSED"
            return "DISTRACTED"

        if score >= self.distracted_threshold:
            return "DISTRACTED"

        return "FOCUSED"

    def reset(self):
        pass