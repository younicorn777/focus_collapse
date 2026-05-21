import csv
import os
from datetime import datetime


LOG_DIR = os.path.join(os.path.dirname(__file__), "records")
LOG_FILE = os.path.join(LOG_DIR, "focus_log.csv")

FIELDNAMES = ["date", "timestamp", "state", "score", "reason", "event"]


def ensure_log_file():
    os.makedirs(LOG_DIR, exist_ok=True)

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()


def write_log(data):
    ensure_log_file()

    now = datetime.now()

    row = {
        "date": now.strftime("%Y-%m-%d"),
        "timestamp": data.get("timestamp", now.strftime("%H:%M:%S")),
        "state": data.get("state", ""),
        "score": data.get("score", 0),
        "reason": data.get("reason", ""),
        "event": data.get("event", ""),
    }

    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writerow(row)

    return row


def read_logs():
    ensure_log_file()

    with open(LOG_FILE, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)
