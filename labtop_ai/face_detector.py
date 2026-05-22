import mediapipe as mp


class FaceDetector:
    """
    MediaPipe FaceMesh를 이용해 얼굴 랜드마크를 검출하는 클래스.
    """

    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh

        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def detect(self, rgb_frame):
        """
        RGB frame을 입력받아 얼굴 랜드마크를 반환.
        얼굴이 없으면 None 반환.
        """
        results = self.face_mesh.process(rgb_frame)

        if not results.multi_face_landmarks:
            return None

        return results.multi_face_landmarks[0].landmark

    def close(self):
        self.face_mesh.close()