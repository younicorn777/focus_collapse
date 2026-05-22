import requests

class Sender:
    """
    Raspberry Pi Flask 서버로 상태 데이터를 전송하는 클래스.
    """

    def __init__(self, pi_url):
        self.pi_url = pi_url
        self.last_send_success = False

    def send(self, data):
        """
        data를 Raspberry Pi /update_state로 전송.

        전송 실패 시 프로그램을 멈추지 않고 False 반환.
        """
        try:
            response = requests.post(
                self.pi_url,
                json=data,
                timeout=0.5,
            )

            if response.status_code == 200:
                self.last_send_success = True
                print("[SEND OK]", data["event"], data["state"])
                return True

            self.last_send_success = False
            print("[SEND FAIL]", response.status_code)
            return False

        except requests.exceptions.RequestException as e:
            self.last_send_success = False
            print("[SEND ERROR]", e)
            return False