import datetime
from typing import Tuple

from aw_core import Event as AWEvent
from typing_extensions import TypedDict


class AllEventData(TypedDict):
    id: int
    timestamp: str
    duration: float


class Event:
    def __init__(self, data: AllEventData):
        self.data = data

    @classmethod
    def from_aw_event(cls, event: AWEvent) -> 'Event':
        data: AllEventData = AllEventData(
            id=event.id,
            timestamp=event.timestamp.isoformat(),
            duration=event.duration.total_seconds(),
        )
        return cls(data)

    def __repr__(self) -> str:
        return f"<Event(time={self.time}, duration={self.duration})>"

    @property
    def duration(self) -> float:
        return self.data["duration"]

    @property
    def time(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self.data["timestamp"])

    @property
    def end_time(self) -> datetime.datetime:
        return self.time + datetime.timedelta(seconds=self.duration)

    @property
    def day(self) -> datetime.date:
        return self.time.date()

    @property
    def start_end_duration(self) -> Tuple[datetime.datetime, datetime.datetime, float]:
        return self.time, self.end_time, self.duration