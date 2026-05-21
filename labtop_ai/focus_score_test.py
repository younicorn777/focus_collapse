import time
import math
import cv2
import mediapipe as mp


# =========================
# Landmark Index
# =========================

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

MOUTH = {
    "left": 61,
    "right": 291,
    "top": 13,
    "bottom": 14,
}


# =========================
# Threshold Settings
# =========================

EYE_CLOSED_THRESHOLD = 0.20
EYE_CLOSED_SECONDS = 1.5

MOUTH_OPEN_THRESHOLD = 0.35
YAWN_SECONDS = 2.0

FACE_NOT_FOUND_SECONDS = 5.0

SCORE_MIN = 0
SCORE_MAX = 100

EYE_CLOSED_SCORE = 25
YAWN_SCORE = 30
NORMAL_RECOVERY_SCORE = 10

COLLAPSED_SCORE_THRESHOLD = 60
COLLAPSED_HOLD_SECONDS = 5.0


# =========================
# Utility Functions
# =========================

def distance(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


def get_eye_ratio(landmarks, eye):
    left = landmarks[eye["left"]]
    right = landmarks[eye["right"]]
    top = landmarks[eye["top"]]
    bottom = landmarks[eye["bottom"]]

    horizontal = distance(left, right)
    vertical = distance(top, bottom)

    if horizontal == 0:
        return 0

    return vertical / horizontal


def get_mouth_ratio(landmarks):
    left = landmarks[MOUTH["left"]]
    right = landmarks[MOUTH["right"]]
    top = landmarks[MOUTH["top"]]
    bottom = landmarks[MOUTH["bottom"]]

    horizontal = distance(left, right)
    vertical = distance(top, bottom)

    if horizontal == 0:
        return 0

    return vertical / horizontal


def get_state_from_score(score, collapsed_candidate_duration):
    if score >= COLLAPSED_SCORE_THRESHOLD:
        if collapsed_candidate_duration >= COLLAPSED_HOLD_SECONDS:
            return "COLLAPSED"
        return "COLLAPSED_CANDIDATE"

    if score >= 30:
        return "DISTRACTED"

    return "FOCUSED"


def main():
    mp_face_mesh = mp.solutions.face_mesh

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        return

    focus_score = 0

    eye_closed_start_time = None
    eye_event_triggered = False

    mouth_open_start_time = None
    yawn_event_triggered = False

    face_not_found_start_time = None

    collapsed_candidate_start_time = None

    last_normal_recovery_time = time.time()
    last_state = None

    print("Focus Collapse Score 테스트 실행 중입니다.")
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

            current_time = time.time()

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = face_mesh.process(rgb_frame)

            reason_text = "normal"
            event_text = "none"

            if results.multi_face_landmarks:
                face_not_found_start_time = None

                face_landmarks = results.multi_face_landmarks[0]
                landmarks = face_landmarks.landmark

                left_eye_ratio = get_eye_ratio(landmarks, LEFT_EYE)
                right_eye_ratio = get_eye_ratio(landmarks, RIGHT_EYE)
                eye_ratio = (left_eye_ratio + right_eye_ratio) / 2

                mouth_ratio = get_mouth_ratio(landmarks)

                is_eye_closed = eye_ratio < EYE_CLOSED_THRESHOLD
                is_mouth_open = mouth_ratio > MOUTH_OPEN_THRESHOLD

                # =========================
                # Eye Closed Event
                # =========================
                if is_eye_closed:
                    if eye_closed_start_time is None:
                        eye_closed_start_time = current_time

                    eye_closed_duration = current_time - eye_closed_start_time

                    if eye_closed_duration >= EYE_CLOSED_SECONDS and not eye_event_triggered:
                        eye_event_triggered = True
                        focus_score += EYE_CLOSED_SCORE
                        event_text = "eye_closed_event"
                        reason_text = "eye_closed"
                        print(f"eye_closed_event 발생 → score: {focus_score}")

                else:
                    eye_closed_start_time = None
                    eye_event_triggered = False
                    eye_closed_duration = 0

                # =========================
                # Yawn Event
                # =========================
                if is_mouth_open:
                    if mouth_open_start_time is None:
                        mouth_open_start_time = current_time

                    mouth_open_duration = current_time - mouth_open_start_time

                    if mouth_open_duration >= YAWN_SECONDS and not yawn_event_triggered:
                        yawn_event_triggered = True
                        focus_score += YAWN_SCORE
                        event_text = "yawn_event"
                        reason_text = "yawn"
                        print(f"yawn_event 발생 → score: {focus_score}")

                else:
                    mouth_open_start_time = None
                    yawn_event_triggered = False
                    mouth_open_duration = 0

                # =========================
                # Normal Recovery
                # =========================
                if not is_eye_closed and not is_mouth_open:
                    if current_time - last_normal_recovery_time >= 3.0:
                        focus_score -= NORMAL_RECOVERY_SCORE
                        last_normal_recovery_time = current_time
                        reason_text = "normal_recovery"

                focus_score = clamp(focus_score, SCORE_MIN, SCORE_MAX)

                # =========================
                # Collapsed Candidate Duration
                # =========================
                if focus_score >= COLLAPSED_SCORE_THRESHOLD:
                    if collapsed_candidate_start_time is None:
                        collapsed_candidate_start_time = current_time

                    collapsed_candidate_duration = current_time - collapsed_candidate_start_time
                else:
                    collapsed_candidate_start_time = None
                    collapsed_candidate_duration = 0

                state = get_state_from_score(focus_score, collapsed_candidate_duration)

                if state != last_state:
                    print(f"상태 변경: {last_state} → {state}")
                    last_state = state

                # =========================
                # Screen Display
                # =========================
                cv2.putText(
                    frame,
                    f"STATE: {state}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255) if state in ["COLLAPSED", "COLLAPSED_CANDIDATE"] else (0, 255, 0),
                    2,
                )

                cv2.putText(
                    frame,
                    f"Score: {focus_score}",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                )

                cv2.putText(
                    frame,
                    f"Eye Ratio: {eye_ratio:.3f}",
                    (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )

                cv2.putText(
                    frame,
                    f"Mouth Ratio: {mouth_ratio:.3f}",
                    (20, 155),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )

                cv2.putText(
                    frame,
                    f"Reason: {reason_text}",
                    (20, 190),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )

            else:
                # =========================
                # Face Not Found
                # =========================
                eye_closed_start_time = None
                eye_event_triggered = False
                mouth_open_start_time = None
                yawn_event_triggered = False
                collapsed_candidate_start_time = None

                if face_not_found_start_time is None:
                    face_not_found_start_time = current_time

                face_not_found_duration = current_time - face_not_found_start_time

                if face_not_found_duration >= FACE_NOT_FOUND_SECONDS:
                    state = "INVALID"
                else:
                    state = "FACE_NOT_FOUND_WAIT"

                if state != last_state:
                    print(f"상태 변경: {last_state} → {state}")
                    last_state = state

                cv2.putText(
                    frame,
                    f"STATE: {state}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                )

                cv2.putText(
                    frame,
                    f"Face missing: {face_not_found_duration:.1f}s",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                )

            cv2.imshow("Focus Score Test", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()