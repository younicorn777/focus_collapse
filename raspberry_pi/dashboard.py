from datetime import datetime

from logger import read_logs


# ============================================================
# State Groups
# ============================================================

WORK_STATES = ["FOCUSED", "DISTRACTED"]
REST_STATES = ["RESTING"]
ACTIVE_STATES = [
    "FOCUSED",
    "DISTRACTED",
    "COLLAPSED",
    "RESTING",
    "REST_END_ALERT",
    "INVALID",
]


# ============================================================
# Utility
# ============================================================

def parse_time(time_text):
    return datetime.strptime(time_text, "%H:%M:%S")


def format_seconds(seconds):
    seconds = int(seconds)

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def get_description(state, reason, event):
    if state == "FOCUSED":
        return "집중 작업"

    if state == "DISTRACTED":
        return "집중 저하"

    if state == "COLLAPSED":
        return "집중 붕괴 경고"

    if state == "RESTING":
        return "휴식"

    if state == "REST_END_ALERT":
        return "휴식 종료 알림"

    if state == "STOPPED":
        return "작업 종료"

    if state == "INVALID":
        return "얼굴 인식 불가"

    if event:
        return event

    if reason:
        return reason

    return "-"


# ============================================================
# Timetable
# ============================================================

def build_timetable(target_date=None):
    """
    오늘 또는 특정 날짜의 로그를 바탕으로 타임테이블 생성.

    마지막 로그도 누락되지 않도록 처리한다.
    - 마지막 로그가 진행 중 상태이면 현재 시간까지 이어진 것으로 계산
    - 마지막 로그가 STOPPED 같은 종료 상태이면 duration 0으로 표시
    """
    logs = read_logs(target_date)

    if len(logs) == 0:
        return []

    timetable = []

    for i in range(len(logs)):
        current = logs[i]

        start_time = current.get("timestamp", "")
        state = current.get("state", "")
        reason = current.get("reason", "")
        event = current.get("event", "")
        work_id = current.get("work_id", "")

        try:
            start_dt = parse_time(start_time)

            if i < len(logs) - 1:
                next_log = logs[i + 1]
                end_time = next_log.get("timestamp", "")
                end_dt = parse_time(end_time)

            else:
                if state in ACTIVE_STATES:
                    end_dt = datetime.now()
                    end_time = end_dt.strftime("%H:%M:%S")

                else:
                    end_dt = start_dt
                    end_time = start_time

            duration_seconds = (end_dt - start_dt).total_seconds()
            duration_seconds = max(duration_seconds, 0)

        except Exception:
            end_time = start_time
            duration_seconds = 0

        timetable.append({
            "work_id": work_id,
            "start": start_time,
            "end": end_time,
            "state": state,
            "event": event,
            "description": get_description(state, reason, event),
            "duration": format_seconds(duration_seconds),
        })

    return timetable


# ============================================================
# Summary
# ============================================================

def build_summary(target_date=None):
    timetable = build_timetable(target_date)

    work_seconds = 0
    rest_seconds = 0
    focused_seconds = 0
    distracted_seconds = 0
    collapsed_seconds = 0
    invalid_seconds = 0
    collapsed_count = 0

    for item in timetable:
        try:
            duration_parts = item["duration"].split(":")
            duration = (
                int(duration_parts[0]) * 3600
                + int(duration_parts[1]) * 60
                + int(duration_parts[2])
            )

        except Exception:
            duration = 0

        state = item["state"]
        event = item.get("event", "")

        if state in WORK_STATES:
            work_seconds += duration

        if state == "FOCUSED":
            focused_seconds += duration

        elif state == "DISTRACTED":
            distracted_seconds += duration

        elif state == "COLLAPSED":
            collapsed_seconds += duration

            if event == "collapse":
                collapsed_count += 1

        elif state == "INVALID":
            invalid_seconds += duration

        elif state in REST_STATES:
            rest_seconds += duration

    return {
        "total_work_time": format_seconds(work_seconds),
        "focused_time": format_seconds(focused_seconds),
        "distracted_time": format_seconds(distracted_seconds),
        "collapsed_time": format_seconds(collapsed_seconds),
        "invalid_time": format_seconds(invalid_seconds),
        "rest_time": format_seconds(rest_seconds),
        "collapsed_count": collapsed_count,
    }