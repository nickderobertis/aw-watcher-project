import datetime

from aw_client import ActivityWatchClient
from tzlocal import get_localzone

from aw_watcher_project.config import BUCKET_NAME


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


def get_default_end_time() -> datetime.datetime:
    return datetime.datetime.now().replace(
        tzinfo=get_localzone(), hour=23, minute=59, second=59
    )