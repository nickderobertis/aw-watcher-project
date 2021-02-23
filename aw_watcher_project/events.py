import datetime
from collections import defaultdict
from typing import Tuple, List, Dict

from typing_extensions import TypedDict

from aw_watcher_project.exc import ProjectDoesNotExistException


class AllEventData(TypedDict):
    id: int
    timestamp: str
    duration: float


class ProjectData(TypedDict):
    project: str


class ProjectEventData(AllEventData):
    data: ProjectData


class Event:
    def __init__(self, data: AllEventData):
        self.data = data

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


class ProjectEvent(Event):
    data: ProjectEventData

    def __init__(self, data: ProjectEventData):
        super().__init__(data)

    def __repr__(self) -> str:
        return f"<ProjectEvent(project={self.project}, time={self.time}, duration={self.duration})>"

    @property
    def project(self) -> str:
        return self.data["data"]["project"]


def duration_by_project(events: List[ProjectEvent]) -> Dict[str, float]:
    durations: Dict[str, float] = defaultdict(lambda: 0)
    for event in events:
        durations[event.project] += event.duration
    return dict(durations)


def duration_by_day_by_project(
    events: List[ProjectEvent],
) -> Dict[datetime.date, Dict[str, float]]:
    day_data: Dict[datetime.date, Dict[str, float]] = defaultdict(
        lambda: defaultdict(lambda: 0)
    )
    for event in events:
        day_data[event.day][event.project] += event.duration
    day_data = {key: dict(val) for key, val in day_data.items()}
    return dict(day_data)


def start_end_durations_by_project(
    events: List[ProjectEvent],
) -> Dict[str, List[Tuple[datetime.datetime, datetime.datetime, float]]]:
    time_data: Dict[
        str, List[Tuple[datetime.datetime, datetime.datetime, float]]
    ] = defaultdict(lambda: [])
    for event in events:
        time_data[event.project].append(event.start_end_duration)
    return dict(time_data)


def events_by_project(events: List[ProjectEvent]) -> Dict[str, List[ProjectEvent]]:
    events_dict: Dict[str, List[ProjectEvent]] = defaultdict(lambda: [])
    for event in events:
        events_dict[event.project].append(event)
    return dict(events_dict)


class ProjectEvents:
    def __init__(self, events: List[ProjectEventData]):
        self.events = [ProjectEvent(event) for event in events]

    def __getitem__(self, item) -> ProjectEvent:
        return self.events[item]

    def duration_by_project(self) -> Dict[str, float]:
        return duration_by_project(self.events)

    def duration_by_day_by_project(self) -> Dict[datetime.date, Dict[str, float]]:
        return duration_by_day_by_project(self.events)

    def start_end_durations_by_project(
        self,
    ) -> Dict[str, List[Tuple[datetime.datetime, datetime.datetime, float]]]:
        return start_end_durations_by_project(self.events)

    def events_by_project(self) -> Dict[str, List[ProjectEvent]]:
        return events_by_project(self.events)

    def events_for_project(self, project: str) -> List[ProjectEvent]:
        events_dict = self.events_by_project()
        try:
            return events_dict[project]
        except KeyError:
            raise ProjectDoesNotExistException(project)
