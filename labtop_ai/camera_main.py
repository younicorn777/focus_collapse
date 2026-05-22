import time
import cv2

from face_detector import FaceDetector
from eye_detector import EyeDetector
from yawn_detector import YawnDetector
from score_manager import ScoreManager
from focus_session import FocusSession
from sender import Sender


PI_URL = "http://라즈베리파이IP:5000/update_state"
# 예: PI_URL = "http://192.168.0.25:5000/update_state"

HEARTBEAT_INTERVAL = 1.0
FACE_NOT_FOUND_SECONDS = 5.0


def put_text(frame, text, y, color=(255, 255, 255), scale=0.7):
    cv2.putText(
        frame,
        text,
        (20, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        2,
    )


def send_event(sender, session, event):
    payload = session.make_payload(event=event)
    sender.send(payload)


def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        return

    face_detector = FaceDetector()
    eye_detector = EyeDetector()
    yawn_detector = YawnDetector()
    score_manager = ScoreManager()
    session = FocusSession(rest_seconds=20)
    sender = Sender(PI_URL)

    last_heartbeat_time = 0
    face_not_found_start_time = None

    print("Focus Collapse AI 실행 중")
    print("s: 작업 시작")
    print("x: 작업 종료")
    print("r: 휴식 시작")
    print("e: 휴식 종료 후 복귀")
    print("q: 종료")

    send_event(sender, session, "program_start")

    try:
        while True:
            current_time = time.time()

            ret, frame = cap.read()

            if not ret:
                print("프레임을 읽을 수 없습니다.")
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                session.stop_work()
                send_event(sender, session, "program_quit")
                break

            elif key == ord("s"):
                event = session.start_work()

                if event != "ignored":
                    score_manager.reset()
                    eye_detector.reset()
                    yawn_detector.reset()
                    face_not_found_start_time = None

                    send_event(sender, session, event)
                    print("[KEY] s → start_work")

            elif key == ord("x"):
                event = session.stop_work()

                if event != "ignored":
                    face_not_found_start_time = None

                    send_event(sender, session, event)
                    print("[KEY] x → stop_work")

            elif key == ord("r"):
                event = session.start_rest()

                if event != "ignored":
                    face_not_found_start_time = None

                    send_event(sender, session, event)
                    print("[KEY] r → rest_start")

            elif key == ord("e"):
                event = session.end_rest()

                if event != "ignored":
                    score_manager.reset()
                    eye_detector.reset()
                    yawn_detector.reset()
                    face_not_found_start_time = None

                    send_event(sender, session, event)
                    print("[KEY] e → resume_work")

            timer_event = session.update_timer()

            if timer_event != "none":
                send_event(sender, session, timer_event)
                print("[TIMER]", timer_event)

            eye_ratio = 0.0
            mouth_ratio = 0.0
            eye_duration = 0.0
            mouth_duration = 0.0

            ai_enabled = (
                session.state in ["FOCUSED", "DISTRACTED", "INVALID"]
                and not session.collapsed_locked
            )

            if ai_enabled:
                landmarks = face_detector.detect(rgb_frame)

                if landmarks is None:
                    if face_not_found_start_time is None:
                        face_not_found_start_time = current_time

                    missing_duration = current_time - face_not_found_start_time

                    if missing_duration >= FACE_NOT_FOUND_SECONDS:
                        if session.state != "INVALID":
                            session.state = "INVALID"
                            session.reason = "face_not_found"

                            send_event(sender, session, "face_not_found")
                            print("[AI] FACE NOT FOUND")

                else:
                    face_not_found_start_time = None

                    eye_result = eye_detector.update(landmarks)
                    yawn_result = yawn_detector.update(landmarks)

                    eye_ratio = eye_result["ratio"]
                    mouth_ratio = yawn_result["ratio"]
                    eye_duration = eye_result["duration"]
                    mouth_duration = yawn_result["duration"]

                    if yawn_result["is_open"]:
                        eye_risk_for_score = False
                    else:
                        eye_risk_for_score = eye_result["risk"]

                    yawn_event = yawn_result["event"]

                    normal = (
                        not eye_result["is_closed"]
                        and not yawn_result["is_open"]
                    )

                    score_result = score_manager.update(
                        eye_risk=eye_risk_for_score,
                        yawn_event=yawn_event,
                        normal=normal,
                    )

                    score = score_result["score"]
                    reason = score_result["reason"]

                    ai_event = session.update_ai_state(
                        score=score,
                        reason=reason,
                    )

                    if ai_event in ["state_change", "collapse"]:
                        send_event(sender, session, ai_event)
                        print("[AI]", ai_event, session.state, session.score)

            if current_time - last_heartbeat_time >= HEARTBEAT_INTERVAL:
                send_event(sender, session, "heartbeat")
                last_heartbeat_time = current_time

            state = session.state
            score = session.score
            work_time = session.get_current_work_seconds()
            rest_left = session.get_rest_left_seconds()

            if state == "COLLAPSED":
                state_color = (0, 0, 255)
            elif state == "DISTRACTED":
                state_color = (0, 255, 255)
            elif state == "RESTING":
                state_color = (255, 0, 0)
            elif state == "REST_END_ALERT":
                state_color = (255, 0, 255)
            elif state == "STOPPED":
                state_color = (180, 180, 180)
            elif state == "INVALID":
                state_color = (100, 100, 255)
            else:
                state_color = (0, 255, 0)

            put_text(frame, f"STATE: {state}", 40, state_color, 1.0)
            put_text(frame, f"Score: {score}", 80)
            put_text(frame, f"Work ID: {session.work_id}", 115)
            put_text(frame, f"Work Time: {int(work_time)}s", 150)

            if state in ["RESTING", "REST_END_ALERT"]:
                put_text(frame, f"Rest Left: {int(rest_left)}s", 185)

            put_text(frame, f"Eye Ratio: {eye_ratio:.3f}", 220)
            put_text(frame, f"Eye Closed: {eye_duration:.1f}s", 255)
            put_text(frame, f"Mouth Ratio: {mouth_ratio:.3f}", 290)
            put_text(frame, f"Mouth Open: {mouth_duration:.1f}s", 325)
            put_text(
                frame,
                "Keys: s=start x=stop r=rest e=end q=quit",
                460,
                (200, 200, 200),
                0.6,
            )

            cv2.imshow("Focus Collapse AI", frame)

    finally:
        try:
            sender.close()
        except:
            pass

        cap.release()
        face_detector.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()