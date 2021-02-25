from typing import TypedDict, List, Generator

from aw_watcher_project.events.window import WindowEventData, WindowEvent


class ActivityData(TypedDict):
    aw_watcher_window_events: List[WindowEventData]


class Activity:
    def __init__(self, events: List[WindowEventData]):
        self.events = [WindowEvent(event) for event in events]

    def __getitem__(self, item) -> WindowEvent:
        return self.events[item]

    def __iter__(self) -> Generator[WindowEvent, WindowEvent, None]:
        yield from self.events

    @classmethod
    def from_events(cls, events: List[WindowEvent]):
        obj = cls([])
        obj.events = events
        return obj

    def for_app(self, name: str) -> 'Activity':
        events = [event for event in self if event.app == name]
        return self.__class__.from_events(events)

    @property
    def titles(self) -> List[str]:
        return [event.title for event in self]