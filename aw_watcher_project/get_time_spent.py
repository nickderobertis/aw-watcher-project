import datetime
from collections import defaultdict
from typing_extensions import TypedDict
from typing import List, Dict, Optional, Tuple
import pytz
from tzlocal import get_localzone

from aw_client import ActivityWatchClient

from aw_watcher_project.config import BUCKET_NAME
from aw_watcher_project.exc import ProjectDoesNotExistException


class ProjectData(TypedDict):
    project: str


class ProjectEventData(TypedDict):
    id: int
    timestamp: str
    duration: float
    data: ProjectData


class ProjectEvent:
    def __init__(self, data: ProjectEventData):
        self.data = data

    def __repr__(self) -> str:
        return f'<ProjectEvent(project={self.project}, time={self.time}, duration={self.duration})>'

    @property
    def duration(self) -> float:
        return self.data["duration"]

    @property
    def project(self) -> str:
        return self.data["data"]["project"]

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


def get_begin_time(bucket_name: str = BUCKET_NAME) -> datetime.datetime:
    client = ActivityWatchClient()
    buckets = client.get_buckets()
    selected_bucket = None
    for bucket in buckets.values():
        if bucket["id"] == bucket_name + "_" + bucket["hostname"]:
            selected_bucket = bucket
    if selected_bucket is None:
        raise ValueError(f"bucket {bucket_name} does not exist, run project watcher")

    return datetime.datetime.fromisoformat(selected_bucket["created"]).replace(
        tzinfo=get_localzone(), hour=0, minute=0, second=0
    )


def get_events(
    begin: Optional[datetime.datetime] = None, end: Optional[datetime.datetime] = None
) -> ProjectEvents:
    if begin is None:
        begin = get_begin_time()
    if end is None:
        end = datetime.datetime.now().replace(
            tzinfo=get_localzone(), hour=23, minute=59, second=59
        )
    time_periods = [(begin, end)]
    client = ActivityWatchClient()
    events: List[List[ProjectEventData]] = client.query(
        """
afk_events = query_bucket(find_bucket("aw-watcher-afk_"));
project_events = query_bucket(find_bucket("aw-watcher-project-selected_"));
project_events = filter_period_intersect(project_events, filter_keyvals(afk_events, "status", ["not-afk"]));
RETURN = project_events;
       """,
        time_periods,
    )
    return ProjectEvents(events[0])


if __name__ == "__main__":
    project_events = get_events()
    print(project_events.duration_by_project())
    print(project_events.duration_by_day_by_project())
    print(project_events.start_end_durations_by_project())
