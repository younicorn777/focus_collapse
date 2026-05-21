class Sender:
    def __init__(self, pi_url=None):
        self.pi_url = pi_url

    def send(self, data):
        # 다음 단계에서 requests.post()로 구현 예정
        print("[SEND MOCK]", data)