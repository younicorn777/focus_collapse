import time

from lcd import LCDController


def main():
    lcd = LCDController()

    test_statuses = [
        {
            "state": "STOPPED",
            "current_work_seconds": 0,
            "rest_left_seconds": 0,
        },
        {
            "state": "FOCUSED",
            "current_work_seconds": 12,
            "rest_left_seconds": 0,
        },
        {
            "state": "DISTRACTED",
            "current_work_seconds": 35,
            "rest_left_seconds": 0,
        },
        {
            "state": "COLLAPSED",
            "current_work_seconds": 50,
            "rest_left_seconds": 0,
        },
        {
            "state": "RESTING",
            "current_work_seconds": 50,
            "rest_left_seconds": 10,
        },
        {
            "state": "REST_END_ALERT",
            "current_work_seconds": 50,
            "rest_left_seconds": 0,
        },
        {
            "state": "INVALID",
            "current_work_seconds": 50,
            "rest_left_seconds": 0,
        },
    ]

    for status in test_statuses:
        lcd.update_by_status(status)
        time.sleep(1)


if __name__ == "__main__":
    main()