import os
import csv
from datetime import datetime


# ============================================================
# Records Directory
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "records")

os.makedirs(LOG_DIR, exist_ok=True)


# ============================================================
# CSV Header
# ============================================================

CSV_COLUMNS = [
    "date",
    "timestamp",
    "state",
    "score",
    "reason",
    "event",
    "work_id",
]


# ============================================================
# Log File Path
# ============================================================

def get_log_file(target_date=None):
    """
    날짜별 CSV 파일 경로 반환.

    예:
    records/focus_log_2026-05-21.csv
    """
    if target_date is None:
        target_date = datetime.now().strftime("%Y-%m-%d")

    filename = f"focus_log_{target_date}.csv"

    return os.path.join(LOG_DIR, filename)


# ============================================================
# File Creation
# ============================================================

def ensure_log_file(target_date=None):
    """
    날짜별 CSV 파일이 없으면 새로 생성하고 헤더 작성.
    """
    log_file = get_log_file(target_date)

    if not os.path.exists(log_file):
        with open(log_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()

    return log_file


# ============================================================
# Write Log
# ============================================================

def write_log(row):
    """
    CSV에 로그 1개 추가.

    row 예:
    {
        "timestamp": "14:20:10",
        "state": "FOCUSED",
        "score": 10,
        "reason": "normal",
        "event": "start_work",
        "work_id": 1,
    }
    """
    today = datetime.now().strftime("%Y-%m-%d")

    log_file = ensure_log_file(today)

    full_row = {
        "date": today,
        "timestamp": row.get("timestamp", ""),
        "state": row.get("state", ""),
        "score": row.get("score", 0),
        "reason": row.get("reason", ""),
        "event": row.get("event", ""),
        "work_id": row.get("work_id", ""),
    }

    with open(log_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writerow(full_row)

    return {
        "saved": True,
        "file": os.path.basename(log_file),
        "row": full_row,
    }


# ============================================================
# Read Logs
# ============================================================

def read_logs(target_date=None):
    """
    특정 날짜의 로그 전체 읽기.

    target_date=None이면 오늘 날짜 로그 읽기.
    """
    log_file = get_log_file(target_date)

    if not os.path.exists(log_file):
        return []

    rows = []

    with open(log_file, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            # 숫자 타입 변환
            try:
                row["score"] = int(row.get("score", 0))
            except:
                row["score"] = 0

            try:
                row["work_id"] = int(row.get("work_id", 0))
            except:
                row["work_id"] = 0

            rows.append(row)

    return rows


# ============================================================
# Utility
# ============================================================

def get_available_log_dates():
    """
    저장된 로그 날짜 목록 반환.

    예:
    [
        "2026-05-20",
        "2026-05-21",
    ]
    """
    dates = []

    for filename in os.listdir(LOG_DIR):
        if filename.startswith("focus_log_") and filename.endswith(".csv"):
            date_str = filename.replace("focus_log_", "").replace(".csv", "")
            dates.append(date_str)

    dates.sort()

    return dates