import json
import os
from typing import Any, Dict, List

class EventFileManager:
    FILE_PATH = os.path.join(os.path.dirname(__file__), "events.json")

    @classmethod
    def read_events_from_file(cls) -> List[Dict[str, Any]]:
        try:
            if not os.path.exists(cls.FILE_PATH):
                return []
            with open(cls.FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                return data
            if isinstance(data, dict) and isinstance(data.get("events"), list):
                return data["events"]
            return []
        except Exception:
            return []

    @classmethod
    def write_events_to_file(cls, events: List[Dict[str, Any]]) -> None:
        os.makedirs(os.path.dirname(cls.FILE_PATH), exist_ok=True)
        with open(cls.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
