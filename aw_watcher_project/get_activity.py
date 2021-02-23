import datetime
from typing import Optional, Sequence, List

from aw_client import ActivityWatchClient

from aw_watcher_project.aw_time import get_begin_time, get_default_end_time
from aw_watcher_project.events.activity import Activity, ActivityData

DEFAULT_ACTIVITY_BUCKETS = ('aw-watcher-window_',)


def _bucket_name_to_event_name(name: str) -> str:
    return name.replace('-', '_') + 'events'


def _bucket_query(name: str, project_name: str) -> str:
    event_name = _bucket_name_to_event_name(name)
    query = f"""
{event_name} = query_bucket(find_bucket("{name}"));
{event_name} = filter_period_intersect({event_name}, filter_keyvals(project_events, "project", ["{project_name}"]));
""".strip()
    return query


def _get_query_return_value(activity_buckets: Sequence[str]) -> str:
    event_names = [_bucket_name_to_event_name(name) for name in activity_buckets]
    key_value_pairs = [f'"{name}": {name}' for name in event_names]
    return 'RETURN = {' + ', '.join(key_value_pairs) + '};'


def _get_activity_query(project: str, activity_buckets: Sequence[str] = DEFAULT_ACTIVITY_BUCKETS) -> str:
    bucket_queries = '\n'.join([_bucket_query(bucket, project) for bucket in activity_buckets])
    query = f"""
afk_events = query_bucket(find_bucket("aw-watcher-afk_"));
project_events = query_bucket(find_bucket("aw-watcher-project-selected_"));
project_events = filter_keyvals(project_events, "project", ["{project}"]);
project_events = filter_period_intersect(project_events, filter_keyvals(afk_events, "status", ["not-afk"]));
{bucket_queries}
{_get_query_return_value(activity_buckets)}
       """.strip()
    return query


def get_activity(
    project: str, begin: Optional[datetime.datetime] = None, end: Optional[datetime.datetime] = None,
    activity_buckets: Sequence[str] = DEFAULT_ACTIVITY_BUCKETS
) -> Activity:
    if begin is None:
        begin = get_begin_time()
    if end is None:
        end = get_default_end_time()
    time_periods = [(begin, end)]
    client = ActivityWatchClient()
    query = _get_activity_query(project, activity_buckets)
    events: List[ActivityData] = client.query(query, time_periods)
    return Activity(events[0]['aw_watcher_window_events'])


if __name__ == '__main__':
    begin = datetime.datetime(2021, 2, 22)
    resp = get_activity('awproject-watcher', begin=begin)
    print(resp.events)
