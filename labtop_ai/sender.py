import requests
class Sender:
    def __init__(self, pi_url="http://172.16.42.59:5000/update_state"):
        self.pi_url = pi_url

    def send(self, data):
        try:
            response = requests.post(self.pi_url, json=data, timeout=1)
            print("[SEND]", data, "status:", response.status_code)

        except requests.exceptions.RequestException as e:
            print("[SEND ERROR]", e)