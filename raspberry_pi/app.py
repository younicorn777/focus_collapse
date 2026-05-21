from flask import Flask, request, jsonify, render_template_string

from logger import write_log, read_logs
from dashboard import build_summary, build_timetable


app = Flask(__name__)

latest_data = {}


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
        .state-focused {
            color: green;
            font-weight: bold;
        }
        .state-distracted {
            color: orange;
            font-weight: bold;
        }
        .state-collapsed {
            color: red;
            font-weight: bold;
        }
        .state-resting {
            color: blue;
            font-weight: bold;
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
        <p>수동 휴식 횟수: <b>{{ summary.manual_rest_count }}회</b></p>
    </div>

    <div class="card">
        <h2>오늘의 작업·휴식 타임테이블</h2>
        <table>
            <thead>
                <tr>
                    <th>시간</th>
                    <th>상태</th>
                    <th>내용</th>
                </tr>
            </thead>
            <tbody>
                {% for item in timetable %}
                <tr>
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
        return jsonify({"status": "error", "message": "No JSON received"}), 400

    latest_data = data

    saved_row = write_log(data)

    print("[RECEIVED]", data)
    print("[SAVED]", saved_row)

    return jsonify({
        "status": "success",
        "received": data,
        "saved": saved_row,
    })


@app.route("/latest", methods=["GET"])
def latest():
    return jsonify(latest_data)


@app.route("/logs", methods=["GET"])
def logs():
    return jsonify(read_logs())


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)