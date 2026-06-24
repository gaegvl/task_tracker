from datetime import datetime

from src.application.ports.clock import ClockPort


class SystemClock(ClockPort):
    def now(self) -> datetime:
        return datetime.now()
