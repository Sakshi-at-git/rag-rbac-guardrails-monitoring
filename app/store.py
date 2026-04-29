from datetime import datetime, timezone
from threading import Lock
from typing import List


class AuditStore:
    def __init__(self) -> None:
        self._records: List[dict] = []
        self._lock = Lock()

    def log(self, event_type: str, actor: str, details: dict) -> None:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "actor": actor,
            "details": details,
        }
        with self._lock:
            self._records.append(event)

    def recent(self, limit: int = 50) -> List[dict]:
        with self._lock:
            return list(reversed(self._records[-limit:]))
