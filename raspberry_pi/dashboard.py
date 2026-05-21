from datetime import datetime, date
from logger import read_logs


WORK_STATES = ["FOCUSED", "DISTRACTED", "COLLAPSED"]
REST_STATES = ["RESTING"]


def parse_time(time_text):
    return datetime.strptime(time_text, "%H:%M:%S")


def format_seconds(seconds):
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def get_today_logs():
    today = date.today().strftime("%Y-%m-%d")
    logs = read_logs()
    return [log for log in logs if log.get("date") == today]


def build_timetable():
    logs = get_today_logs()

    if len(logs) < 2:
        return []

    timetable = []

    for i in range(len(logs) - 1):
        current = logs[i]
        next_log = logs[i + 1]

        start_time = current["timestamp"]
        end_time = next_log["timestamp"]
        state = current["state"]
        reason = current.get("reason", "")

        if state == "FOCUSED":
            description = "집중 작업"
        elif state == "DISTRACTED":
            description = "집중 저하"
        elif state == "COLLAPSED":
            description = "집중 붕괴 경고"
        elif state == "RESTING":
            description = "휴식"
        elif state == "STOPPED":
            description = "작업 정지"
        elif state == "INVALID":
            description = "얼굴 인식 불가"
        else:
            description = reason

        timetable.append({
            "start": start_time,
            "end": end_time,
            "state": state,
            "description": description,
        })

    return timetable


def build_summary():
    timetable = build_timetable()

    work_seconds = 0
    rest_seconds = 0
    focused_seconds = 0
    distracted_seconds = 0
    collapsed_count = 0
    manual_rest_count = 0

    for item in timetable:
        try:
            start = parse_time(item["start"])
            end = parse_time(item["end"])
            duration = (end - start).total_seconds()
        except Exception:
            duration = 0

        state = item["state"]

        if state in WORK_STATES:
            work_seconds += duration

        if state == "FOCUSED":
            focused_seconds += duration

        if state == "DISTRACTED":
            distracted_seconds += duration

        if state in REST_STATES:
            rest_seconds += duration

        if state == "COLLAPSED":
            collapsed_count += 1

        if state == "RESTING" and item["description"] == "수동 휴식":
            manual_rest_count += 1

    return {
        "total_work_time": format_seconds(work_seconds),
        "focused_time": format_seconds(focused_seconds),
        "distracted_time": format_seconds(distracted_seconds),
        "rest_time": format_seconds(rest_seconds),
        "collapsed_count": collapsed_count,
        "manual_rest_count": manual_rest_count,
    }