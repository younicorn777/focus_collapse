import time
import cv2

from face_detector import FaceDetector
from eye_detector import EyeDetector
from yawn_detector import YawnDetector
from score_manager import ScoreManager
from state_manager import StateManager
from sender import Sender


FACE_NOT_FOUND_SECONDS = 5.0


def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        return

    face_detector = FaceDetector()
    eye_detector = EyeDetector()
    yawn_detector = YawnDetector()
    score_manager = ScoreManager()
    state_manager = StateManager()
    sender = Sender()

    last_state = None
    face_not_found_start_time = None

    print("Focus Collapse 메인 테스트 실행 중입니다.")
    print("종료하려면 q를 누르세요.")

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                print("프레임을 읽을 수 없습니다.")
                break

            current_time = time.time()

            # 거울처럼 보기 위해 좌우 반전
            frame = cv2.flip(frame, 1)

            # OpenCV는 BGR, MediaPipe는 RGB 사용
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 얼굴 랜드마크 검출
            landmarks = face_detector.detect(rgb_frame)

            if landmarks is None:
                # 얼굴이 안 보이면 감지 타이머 초기화
                eye_detector.reset()
                yawn_detector.reset()
                state_manager.reset()

                if face_not_found_start_time is None:
                    face_not_found_start_time = current_time

                missing_duration = current_time - face_not_found_start_time

                if missing_duration >= FACE_NOT_FOUND_SECONDS:
                    state = "INVALID"
                else:
                    state = "FACE_NOT_FOUND_WAIT"

                score = score_manager.score
                reason = "face_not_found"
                eye_ratio = 0.0
                mouth_ratio = 0.0
                eye_duration = 0.0
                mouth_duration = 0.0

            else:
                # 얼굴이 다시 보이면 얼굴 미검출 타이머 초기화
                face_not_found_start_time = None

                # 눈 감김 감지
                eye_result = eye_detector.update(landmarks)

                # 하품 감지
                yawn_result = yawn_detector.update(landmarks)

                # 정상 상태 여부
                # 눈 감김 상태도 아니고, 입 벌림 상태도 아니면 정상으로 판단
                normal = not eye_result["is_closed"] and not yawn_result["is_open"]

                # 점수 계산
                # 눈 감김은 risk=True 상태에서 1초마다 점수 증가
                # 하품은 event=True일 때 1회 점수 증가
                score_result = score_manager.update(
                    eye_risk=eye_result["risk"],
                    yawn_event=yawn_result["event"],
                    normal=normal,
                )

                score = score_result["score"]
                reason = score_result["reason"]

                # COLLAPSED 판단용 이상행동
                # score >= 60 상태에서 eye_risk 또는 yawn_event가 있으면 COLLAPSED
                abnormal_detected = eye_result["risk"] or yawn_result["event"]

                # 상태 판단
                state = state_manager.update(score, abnormal_detected)

                eye_ratio = eye_result["ratio"]
                mouth_ratio = yawn_result["ratio"]
                eye_duration = eye_result["duration"]
                mouth_duration = yawn_result["duration"]

                # 주요 이벤트는 화면이 아니라 터미널에만 출력
                if reason in ["eye_closed", "yawn", "eye_closed+yawn"]:
                    print(f"[EVENT] {reason} → score: {score}")

            # 상태가 바뀐 경우에만 전송/출력
            if state != last_state:
                data = {
                    "state": state,
                    "score": score,
                    "reason": reason,
                    "event": "state_change",
                    "timestamp": time.strftime("%H:%M:%S"),
                }

                sender.send(data)
                print(f"상태 변경: {last_state} → {state}")
                last_state = state

            # =========================
            # 화면 표시
            # =========================

            # 상태 색상
            if state in ["COLLAPSED", "INVALID"]:
                state_color = (0, 0, 255) # 빨간색
            elif state == "DISTRACTED":
                state_color = (0, 255, 255) # 노란색
            else:
                state_color = (0, 255, 0) # 초록색

            cv2.putText(
                frame,
                f"STATE: {state}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                state_color,
                2,
            )

            cv2.putText(
                frame,
                f"Score: {score}",
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
                f"Eye Closed: {eye_duration:.1f}s",
                (20, 155),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"Mouth Ratio: {mouth_ratio:.3f}",
                (20, 190),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"Mouth Open: {mouth_duration:.1f}s",
                (20, 225),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.imshow("Focus Collapse Main", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        cap.release()
        face_detector.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()