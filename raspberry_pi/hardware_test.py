import time

from hardware import HardwareController


def main():
    hardware = HardwareController()

    test_states = [
        "STOPPED",
        "FOCUSED",
        "DISTRACTED",
        "COLLAPSED",
        "RESTING",
        "REST_END_ALERT",
        "INVALID",
    ]

    for state in test_states:
        print()
        print("현재 상태:", state)
        hardware.update_led_by_state(state)
        time.sleep(1)


if __name__ == "__main__":
    main()