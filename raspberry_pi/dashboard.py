from datetime import datetime
from logger import read_logs


# ============================================================
# State Groups
# ============================================================

WORK_STATES = ["FOCUSED", "DISTRACTED", "COLLAPSED"]
REST_STATES = ["RESTING"]


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
    read_logs()는 기본적으로 오늘 날짜 CSV만 읽는다.
    """
    logs = read_logs(target_date)

    if len(logs) < 2:
        return []

    timetable = []

    for i in range(len(logs) - 1):
        current = logs[i]
        next_log = logs[i + 1]

        start_time = current.get("timestamp", "")
        end_time = next_log.get("timestamp", "")

        state = current.get("state", "")
        reason = current.get("reason", "")
        event = current.get("event", "")
        work_id = current.get("work_id", "")

        try:
            start_dt = parse_time(start_time)
            end_dt = parse_time(end_time)
            duration_seconds = (end_dt - start_dt).total_seconds()

            if duration_seconds < 0:
                duration_seconds = 0

        except Exception:
            duration_seconds = 0

        timetable.append({
            "work_id": work_id,
            "start": start_time,
            "end": end_time,
            "state": state,
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

        if state in WORK_STATES:
            work_seconds += duration

        if state == "FOCUSED":
            focused_seconds += duration

        elif state == "DISTRACTED":
            distracted_seconds += duration

        elif state == "COLLAPSED":
            collapsed_seconds += duration
            collapsed_count += 1

        elif state in REST_STATES:
            rest_seconds += duration

    return {
        "total_work_time": format_seconds(work_seconds),
        "focused_time": format_seconds(focused_seconds),
        "distracted_time": format_seconds(distracted_seconds),
        "collapsed_time": format_seconds(collapsed_seconds),
        "rest_time": format_seconds(rest_seconds),
        "collapsed_count": collapsed_count,
    }