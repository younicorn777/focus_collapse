import time
from flask import Flask, request, jsonify, render_template_string

from hardware import HardwareController
from lcd import LCDController
from logger import write_log, read_logs
from dashboard import build_summary, build_timetable


app = Flask(__name__)

hardware = HardwareController()
lcd = LCDController()

latest_data = {
    "state": "STOPPED",
    "score": 0,
    "reason": "ready",
    "event": "init",
    "work_id": 0,
    "work_seconds": 0,
    "rest_left_seconds": 0,
}


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Focus Collapse Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background: #f7f7f7;
        }
        h1, h2 {
            color: #222;
        }
        .card {
            background: white;
            padding: 20px;
            margin-bottom: 24px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }
        th, td {
            border-bottom: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }
        th {
            background: #eee;
        }
    </style>
</head>
<body>
    <h1>🧠 Focus Collapse Dashboard</h1>

    <div class="card">
        <h2>오늘 요약</h2>
        <p>총 작업 시간: <b>{{ summary.total_work_time }}</b></p>
        <p>집중 상태 시간: <b>{{ summary.focused_time }}</b></p>
        <p>집중 저하 시간: <b>{{ summary.distracted_time }}</b></p>
        <p>휴식 시간: <b>{{ summary.rest_time }}</b></p>
        <p>집중 붕괴 감지 횟수: <b>{{ summary.collapsed_count }}회</b></p>
    </div>

    <div class="card">
        <h2>오늘의 작업·휴식 타임테이블</h2>
        <table>
            <thead>
                <tr>
                    <th>작업 번호</th>
                    <th>시간</th>
                    <th>상태</th>
                    <th>내용</th>
                </tr>
            </thead>
            <tbody>
                {% for item in timetable %}
                <tr>
                    <td>{{ item.work_id }}</td>
                    <td>{{ item.start }} ~ {{ item.end }}</td>
                    <td>{{ item.state }}</td>
                    <td>{{ item.description }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""


def format_seconds(seconds):
    seconds = int(seconds)

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def build_lcd_status(data):
    """
    lcd.py가 이해하는 형태로 데이터 변환
    """
    return {
        "state": data.get("state", "STOPPED"),
        "current_work_seconds": data.get("work_seconds", 0),
        "rest_left_seconds": data.get("rest_left_seconds", 0),
    }


def sync_outputs(data):
    """
    노트북에서 받은 상태를 하드웨어에 그대로 반영
    """
    state = data.get("state", "STOPPED")

    hardware.update_by_state(state)
    lcd.update_by_status(build_lcd_status(data))


def save_if_event(data):
    """
    이벤트가 있을 때만 CSV 저장.
    heartbeat/status_update는 저장하지 않음.
    """
    event = data.get("event", "")

    if event in ["heartbeat", "status_update", "none", ""]:
        return None

    row = {
        "timestamp": data.get("timestamp", time.strftime("%H:%M:%S")),
        "state": data.get("state", ""),
        "score": data.get("score", 0),
        "reason": data.get("reason", ""),
        "event": event,
        "work_id": data.get("work_id", ""),
    }

    return write_log(row)


@app.route("/")
def dashboard():
    summary = build_summary()
    timetable = build_timetable()

    return render_template_string(
        HTML_TEMPLATE,
        summary=summary,
        timetable=timetable,
    )


@app.route("/update_state", methods=["POST"])
def update_state():
    global latest_data

    data = request.get_json()

    if data is None:
        return jsonify({
            "status": "error",
            "message": "No JSON received"
        }), 400

    latest_data = data

    sync_outputs(data)
    saved = save_if_event(data)

    print("[RECEIVED]", data)

    if saved:
        print("[SAVED]", saved)

    return jsonify({
        "status": "success",
        "received": data,
        "saved": saved,
    })


@app.route("/latest", methods=["GET"])
def latest():
    return jsonify(latest_data)


@app.route("/logs", methods=["GET"])
def logs():
    return jsonify(read_logs())


if __name__ == "__main__":
    try:
        sync_outputs(latest_data)
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=False,
            threaded=True,
        )
    finally:
        hardware.close()
        lcd.close()