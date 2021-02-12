from pathlib import Path
from typing import Union, TypedDict, List

import yaml

from aw_watcher_project.exc import (
    CannotAddProjectException,
    CannotRemoveProjectException,
)
from aw_watcher_project.logger import logger

BUCKET_NAME = "aw-watcher-project-selected"
DEFAULT_CONFIG_DIR = Path.home() / ".aw-watcher-project"
if not DEFAULT_CONFIG_DIR.exists():
    DEFAULT_CONFIG_DIR.mkdir()
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "config.yml"


class ConfigData(TypedDict):
    projects: List[str]


class ProjectWatcherConfig:
    def __init__(self, config_path: Union[str, Path] = DEFAULT_CONFIG_PATH):
        self.config_path = Path(config_path)
        if self.config_path.exists():
            logger.info(f"Loading config from {self.config_path}")
            data: ConfigData = yaml.safe_load(self.config_path.read_text())
            self.projects = data["projects"]
        else:
            logger.info(
                f"No config file exists at {self.config_path}, will create once a project is added"
            )
            if not self.config_path.parent.exists():
                self.config_path.parent.mkdir()
            self.projects = []

    def add_project(self, project: str):
        logger.debug(f"Adding project {project}")
        if project in self.projects:
            raise CannotAddProjectException(f"project {project} already exists")
        self.projects.append(project)
        self.save()

    def remove_project(self, project: str):
        logger.debug(f"Removing project {project}")
        if project not in self.projects:
            raise CannotRemoveProjectException(
                f"project {project} not in existing projects: {self.projects}"
            )
        self.projects.remove(project)
        self.save()

    @property
    def data(self) -> ConfigData:
        return ConfigData(projects=self.projects)

    @property
    def yaml(self) -> str:
        return yaml.safe_dump(self.data)

    def save(self):
        logger.debug(f"Saving config to {self.config_path}")
        self.config_path.write_text(self.yaml)


if __name__ == "__main__":
    import os
    import logging

    logger.setLevel(logging.DEBUG)
    if DEFAULT_CONFIG_PATH.exists():
        os.remove(DEFAULT_CONFIG_PATH)
    config = ProjectWatcherConfig()
    config.add_project("a")
    config.add_project("b")
    config.add_project("c")
    config.remove_project("c")
