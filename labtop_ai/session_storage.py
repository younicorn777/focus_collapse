import json
import os
from datetime import datetime


class SessionStorage:
    """
    날짜별 작업 번호 저장 클래스.

    역할:
    - 오늘 날짜의 session_state_YYYY-MM-DD.json 파일을 읽는다.
    - 오늘 마지막 work_id를 저장한다.
    - 프로그램을 껐다 켜도 같은 날짜의 work_id가 이어지도록 한다.
    """

    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        self.base_dir = base_dir
        self.storage_dir = os.path.join(self.base_dir, "session_records")

        os.makedirs(self.storage_dir, exist_ok=True)

    def get_today(self):
        return datetime.now().strftime("%Y-%m-%d")

    def get_storage_file(self, target_date=None):
        if target_date is None:
            target_date = self.get_today()

        filename = f"session_state_{target_date}.json"
        return os.path.join(self.storage_dir, filename)

    def load_state(self, target_date=None):
        """
        날짜별 상태 파일을 읽는다.
        파일이 없거나 읽기 실패 시 기본값을 반환한다.
        """
        if target_date is None:
            target_date = self.get_today()

        file_path = self.get_storage_file(target_date)

        if not os.path.exists(file_path):
            return {
                "date": target_date,
                "last_work_id": 0,
            }

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            return {
                "date": data.get("date", target_date),
                "last_work_id": int(data.get("last_work_id", 0)),
            }

        except Exception as e:
            print("[SESSION STORAGE ERROR]", e)

            return {
                "date": target_date,
                "last_work_id": 0,
            }

    def save_state(self, last_work_id, target_date=None):
        """
        날짜별 상태 파일에 마지막 work_id를 저장한다.
        """
        if target_date is None:
            target_date = self.get_today()

        os.makedirs(self.storage_dir, exist_ok=True)

        file_path = self.get_storage_file(target_date)

        data = {
            "date": target_date,
            "last_work_id": int(last_work_id),
        }

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

        return data

    def get_last_work_id(self):
        state = self.load_state()
        return state["last_work_id"]

    def update_last_work_id(self, work_id):
        return self.save_state(work_id)