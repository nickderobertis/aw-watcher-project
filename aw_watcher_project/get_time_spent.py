import datetime
from typing import List, Optional
from tzlocal import get_localzone

from aw_client import ActivityWatchClient

from aw_watcher_project.aw_time import get_begin_time, get_default_end_time
from aw_watcher_project.events import ProjectEventData, ProjectEvents


def get_events(
    begin: Optional[datetime.datetime] = None, end: Optional[datetime.datetime] = None
) -> ProjectEvents:
    if begin is None:
        begin = get_begin_time()
    if end is None:
        end = get_default_end_time()
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
