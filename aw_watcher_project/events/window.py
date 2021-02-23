import datetime
from collections import defaultdict
from typing import List, Dict, Tuple

from typing_extensions import TypedDict

from aw_watcher_project.events.base import AllEventData, Event


class WindowData(TypedDict):
    app: str
    title: str


class WindowEventData(AllEventData):
    data: WindowData


class WindowEvent(Event):
    data: WindowEventData

    def __init__(self, data: WindowEventData):
        super().__init__(data)

    def __repr__(self) -> str:
        return f"<WindowEvent(app={self.app}, title={self.title}, time={self.time}, duration={self.duration})>"

    @property
    def app(self) -> str:
        return self.data["data"]["app"]

    @property
    def title(self) -> str:
        return self.data["data"]["title"]