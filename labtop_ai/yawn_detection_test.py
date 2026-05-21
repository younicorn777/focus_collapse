import time
import cv2
import mediapipe as mp
import math


# MediaPipe Face Mesh 기준 입 랜드마크 인덱스
# 입 가로: 61, 291
# 입 세로: 13, 14
MOUTH = {
    "left": 61,
    "right": 291,
    "top": 13,
    "bottom": 14,
}

MOUTH_OPEN_THRESHOLD = 0.35 # 입 벌림 판단 기준값(일반적: 0.3~0.45)
YAWN_SECONDS = 2.0 # 2초 이상 입 벌림 지속 시 하품 이벤트


def distance(p1, p2):
    """두 랜드마크 사이의 거리 계산"""
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


def get_mouth_ratio(landmarks):
    """
    입 세로 길이 / 입 가로 길이 계산
    값이 클수록 입이 크게 벌어진 상태에 가까움
    """
    left = landmarks[MOUTH["left"]]
    right = landmarks[MOUTH["right"]]
    top = landmarks[MOUTH["top"]]
    bottom = landmarks[MOUTH["bottom"]]

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

    mouth_open_start_time = None
    yawn_event_triggered = False

    print("하품 감지 테스트 실행 중입니다.")
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

                mouth_ratio = get_mouth_ratio(landmarks)

                is_mouth_open = mouth_ratio > MOUTH_OPEN_THRESHOLD

                if is_mouth_open:
                    if mouth_open_start_time is None:
                        mouth_open_start_time = current_time

                    open_duration = current_time - mouth_open_start_time

                    if open_duration >= YAWN_SECONDS and not yawn_event_triggered:
                        yawn_event_triggered = True
                        print("yawn_event 발생")

                    status_text = f"MOUTH OPEN {open_duration:.1f}s"

                else:
                    mouth_open_start_time = None
                    yawn_event_triggered = False
                    open_duration = 0
                    status_text = "MOUTH NORMAL"

                cv2.putText(
                    frame,
                    status_text,
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255) if is_mouth_open else (0, 255, 0),
                    2,
                )

                cv2.putText(
                    frame,
                    f"Mouth Ratio: {mouth_ratio:.3f}",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                )

            else:
                mouth_open_start_time = None
                yawn_event_triggered = False

                cv2.putText(
                    frame,
                    "FACE NOT FOUND",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                )

            cv2.imshow("Yawn Detection Test", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()