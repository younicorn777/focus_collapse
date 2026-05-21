import mediapipe as mp


class FaceDetector:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def detect(self, rgb_frame):
        results = self.face_mesh.process(rgb_frame)

        if not results.multi_face_landmarks:
            return None

        return results.multi_face_landmarks[0].landmark

    def close(self):
        self.face_mesh.close()