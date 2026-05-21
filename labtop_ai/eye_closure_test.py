import time
import cv2
import mediapipe as mp
import math


# MediaPipe Face Mesh 기준 눈 랜드마크 인덱스
# 왼쪽 눈
LEFT_EYE = {
    "left": 33,
    "right": 133,
    "top": 159,
    "bottom": 145,
}

# 오른쪽 눈
RIGHT_EYE = {
    "left": 362,
    "right": 263,
    "top": 386,
    "bottom": 374,
}


EYE_CLOSED_THRESHOLD = 0.20   # 눈 감김 판단 기준값(일반적: 0.18~0.23)
EYE_CLOSED_SECONDS = 1.5      # 1.5초 이상 감기면 이벤트 발생


def distance(p1, p2):
    """두 랜드마크 사이의 거리 계산"""
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


def get_eye_ratio(landmarks, eye):
    """
    눈 세로 길이 / 눈 가로 길이 계산
    값이 작을수록 눈이 감긴 상태에 가까움
    """
    left = landmarks[eye["left"]]
    right = landmarks[eye["right"]]
    top = landmarks[eye["top"]]
    bottom = landmarks[eye["bottom"]]

    horizontal = distance(left, right)
    vertical = distance(top, bottom)

    if horizontal == 0:
        return 0

    return vertical / horizontal


def main():
    mp_face_mesh = mp.solutions.face_mesh

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        return

    eye_closed_start_time = None
    eye_event_triggered = False

    print("눈 감김 감지 테스트 실행 중입니다.")
    print("종료하려면 q를 누르세요.")

    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as face_mesh:

        while True:
            ret, frame = cap.read()

            if not ret:
                print("프레임을 읽을 수 없습니다.")
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = face_mesh.process(rgb_frame)

            current_time = time.time()

            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                landmarks = face_landmarks.landmark

                left_eye_ratio = get_eye_ratio(landmarks, LEFT_EYE)
                right_eye_ratio = get_eye_ratio(landmarks, RIGHT_EYE)

                eye_ratio = (left_eye_ratio + right_eye_ratio) / 2

                # 눈 감김 판단
                is_eye_closed = eye_ratio < EYE_CLOSED_THRESHOLD

                if is_eye_closed:
                    if eye_closed_start_time is None:
                        eye_closed_start_time = current_time

                    closed_duration = current_time - eye_closed_start_time

                    if closed_duration >= EYE_CLOSED_SECONDS and not eye_event_triggered:
                        eye_event_triggered = True
                        print("eye_closed_event 발생")

                    status_text = f"EYE CLOSED {closed_duration:.1f}s"

                else:
                    eye_closed_start_time = None
                    eye_event_triggered = False
                    closed_duration = 0
                    status_text = "EYE OPEN"

                # 화면 표시
                cv2.putText(
                    frame,
                    status_text,
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0) if not is_eye_closed else (0, 0, 255),
                    2,
                )

                cv2.putText(
                    frame,
                    f"Eye Ratio: {eye_ratio:.3f}",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                )

            else:
                eye_closed_start_time = None
                eye_event_triggered = False

                cv2.putText(
                    frame,
                    "FACE NOT FOUND",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                )

            cv2.imshow("Eye Closure Test", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()