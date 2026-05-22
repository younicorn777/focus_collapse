import queue
import threading
import requests


class Sender:
    """
    Raspberry Pi Flask 서버로 상태 데이터를 비동기 전송하는 클래스.
    """

    def __init__(self, pi_url, max_queue_size=5):
        self.pi_url = pi_url

        self.queue = queue.Queue(maxsize=max_queue_size)

        self.last_send_success = False

        self.running = True

        self.worker = threading.Thread(
            target=self._worker_loop,
            daemon=True,
        )

        self.worker.start()

    def send(self, data):
        """
        메인 카메라 루프에서는 queue에 넣고 즉시 반환.

        queue가 가득 차면
        가장 오래된 데이터를 버리고 최신 데이터를 유지한다.
        """
        try:
            self.queue.put_nowait(data)

        except queue.Full:
            try:
                self.queue.get_nowait()
                self.queue.put_nowait(data)

            except queue.Empty:
                pass

    def _worker_loop(self):
        """
        백그라운드 전송 worker.
        """

        while self.running or not self.queue.empty():

            try:
                data = self.queue.get(timeout=0.2)

            except queue.Empty:
                continue

            self._send_task(data)

            self.queue.task_done()

    def _send_task(self, data):
        """
        실제 HTTP POST 전송.
        """

        try:
            response = requests.post(
                self.pi_url,
                json=data,
                timeout=0.5,
            )

            if response.status_code == 200:
                self.last_send_success = True

                print(
                    "[SEND OK]",
                    data.get("event"),
                    data.get("state"),
                )

            else:
                self.last_send_success = False

                print(
                    "[SEND FAIL]",
                    response.status_code,
                )

        except requests.exceptions.RequestException as e:
            self.last_send_success = False

            print("[SEND ERROR]", e)

    def close(self):
        """
        sender 종료.

        queue에 남아있는 데이터 전송 후 종료한다.
        """
        self.running = False

        self.worker.join(timeout=2.0)