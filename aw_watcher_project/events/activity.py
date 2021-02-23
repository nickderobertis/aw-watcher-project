from typing import TypedDict, List

from aw_watcher_project.events.window import WindowEventData, WindowEvent


class ActivityData(TypedDict):
    aw_watcher_window_events: List[WindowEventData]


class Activity:
    def __init__(self, events: List[WindowEventData]):
        self.events = [WindowEvent(event) for event in events]

    def __getitem__(self, item) -> WindowEvent:
        return self.events[item]