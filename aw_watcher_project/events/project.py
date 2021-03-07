import datetime
from collections import defaultdict
from typing import List, Dict, Tuple

from typing_extensions import TypedDict

from aw_watcher_project.events.base import AllEventData, Event
from aw_core import Event as AWEvent
from aw_watcher_project.exc import ProjectDoesNotExistException


class ProjectData(TypedDict):
    project: str


class ProjectEventData(AllEventData):
    data: ProjectData


class ProjectEvent(Event):
    data: ProjectEventData

    def __init__(self, data: ProjectEventData):
        super().__init__(data)

    @classmethod
    def from_aw_event(cls, event: AWEvent) -> 'ProjectEvent':
        data: ProjectEventData = ProjectEventData(
            id=event.id,
            timestamp=event.timestamp.isoformat(),
            duration=event.duration.total_seconds(),
            data=ProjectData(
                project=event.data['project']
            )
        )
        return cls(data)

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

    @classmethod
    def from_aw_events(cls, events: List[AWEvent]) -> 'ProjectEvents':
        project_events = [ProjectEvent.from_aw_event(e) for e in events]
        obj = cls([])
        obj.events = project_events
        return obj

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