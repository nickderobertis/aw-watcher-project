from pathlib import Path
from typing import Union

from aw_watcher_project.config import (
    DEFAULT_CONFIG_PATH,
    ProjectWatcherConfig,
)
from aw_watcher_project.gui import ProjectWatcherGUI
from aw_watcher_project.logger import logger


class ProjectWatcherApp:
    def __init__(
        self,
        config_path: Union[str, Path] = DEFAULT_CONFIG_PATH,
        interval: float = 5,
        aw_testing: bool = False,
    ):
        self.config = ProjectWatcherConfig(config_path)
        self.gui = ProjectWatcherGUI(
            self.config, interval=interval, aw_testing=aw_testing
        )


if __name__ == "__main__":
    import logging

    logger.setLevel(logging.DEBUG)
    ProjectWatcherApp(aw_testing=True)
