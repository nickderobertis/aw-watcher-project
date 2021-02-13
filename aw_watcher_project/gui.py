from copy import deepcopy
from datetime import datetime, timezone
from functools import partial
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
from typing import Sequence, Optional, List
from threading import Thread

from PIL import Image, ImageDraw
from PySide6 import QtGui as g
from PySide6 import QtWidgets as w
from aw_core.models import Event
from aw_client import ActivityWatchClient

from aw_watcher_project.config import ProjectWatcherConfig, BUCKET_NAME
from aw_watcher_project.logger import logger


class AddProjectWindow(w.QWidget):
    def __init__(self, gui: "ProjectWatcherGUI", parent: Optional[w.QWidget] = None):
        super().__init__(parent)
        self.gui = gui
        layout = w.QFormLayout()
        self.le = w.QLineEdit()
        self.ok = w.QPushButton("OK")
        self.ok.clicked.connect(self.add_project)
        layout.addRow(self.le, self.ok)
        self.setLayout(layout)
        self.setWindowTitle("Add Project")

    def add_project(self):
        project = self.le.text()
        logger.debug(f"Got project {project} from add project input")
        self.gui.add_project(project)
        self.le.clear()
        self.hide()


class RemoveProjectWindow(w.QWidget):
    def __init__(self, gui: "ProjectWatcherGUI", parent: Optional[w.QWidget] = None):
        super().__init__(parent)
        self.gui = gui
        self._current_projects: Optional[List[str]] = None
        layout = w.QFormLayout()
        self.ok = w.QPushButton("OK")
        self.ok.clicked.connect(self.remove_project)
        self.cb = w.QComboBox()
        self.set_projects()

        layout.addRow(self.cb, self.ok)
        self.setLayout(layout)
        self.setWindowTitle("Remove Project")

    def remove_project(self):
        project = self.cb.currentText()
        logger.debug(f"Got project {project} from remove project input")
        self.gui.remove_project(project)
        self._remove_project_from_dropdown(project)

    def set_projects(self):
        if self._current_projects is not None:
            for project in self._current_projects:
                self.cb.removeItem(0)
        self.cb.addItems(self.gui.config.projects)
        self._current_projects = deepcopy(self.gui.config.projects)

    def _remove_project_from_dropdown(self, project: str):
        if self._current_projects is None:
            raise ValueError("cannot remove projects as not yet set")
        idx = self._current_projects.index(project)
        self.cb.removeItem(idx)
        self._current_projects.remove(project)


def make_text_icon(text: str) -> g.QIcon:
    temp_img = Image.new("RGBA", (200, 100), (255, 0, 0, 0))
    d = ImageDraw.Draw(temp_img)
    text_width, text_height = d.textsize(text)
    img = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((0, 0), text, fill=(255, 255, 255))
    with TemporaryDirectory() as tmp_dir:
        out_path = str(Path(tmp_dir) / "temp.png")
        img.save(out_path)
        icon = g.QIcon(out_path)
    return icon


class ProjectWatcherGUI:
    def __init__(
        self,
        config: ProjectWatcherConfig,
        interval: float = 5,
        aw_testing: bool = False,
    ):
        logger.info("Initializing Project Watcher")
        self.config = config
        self.interval = interval
        self.client = ActivityWatchClient("project-watcher-client", testing=aw_testing)
        self.bucket_id = "{}_{}".format(BUCKET_NAME, self.client.client_hostname)
        self.client.create_bucket(self.bucket_id, event_type="project-selection")
        self.selected_project: Optional[str] = None
        self._hb_thread: Optional[Thread] = None
        self._is_quitting = False
        self._project_actions: List[g.QAction] = []

        self.app = w.QApplication([])
        self.app.setQuitOnLastWindowClosed(False)

        # Adding an icon

        # Adding item on the menu bar
        self.tray = w.QSystemTrayIcon()

        self.menu = w.QMenu()

        # Add N/A option
        self.na = g.QAction("N/A")
        self.na.triggered.connect(self._set_no_project)
        self.menu.addAction(self.na)

        # Add projects
        self._add_project_window = AddProjectWindow(self)
        self.add = g.QAction("Add Project")
        self.add.triggered.connect(self._add_project_window.show)
        self.menu.addAction(self.add)

        # Remove projects
        self._remove_project_window = RemoveProjectWindow(self)
        self.remove = g.QAction("Remove Project")
        self.remove.triggered.connect(self._show_remove_projects)
        self.menu.addAction(self.remove)

        # To quit the app
        quit = g.QAction("Quit")
        quit.triggered.connect(self.quit)
        self.menu.addAction(quit)
        self.tray.setContextMenu(self.menu)

        self.action_group = g.QActionGroup(self.tray, exclusive=True)  # type: ignore
        for project in self.config.projects:
            self._add_project(project)

        self._set_no_project()
        self.tray.setVisible(True)
        logger.info("Starting GUI")
        self.app.exec_()

    def add_project(self, project: str):
        logger.debug(f"add_project called with {project} in GUI")
        self.config.add_project(project)
        self._add_project(project)

    def _add_project(self, project: str):
        option = g.QAction(project, checkable=True)  # type: ignore
        logger.debug(f"Adding project {project} in GUI")
        select_project_func = partial(self._select_project, project)
        option.triggered.connect(select_project_func)
        act = self.action_group.addAction(option)
        self.menu.insertAction(self.na, act)
        self._project_actions.append(act)

    def _show_remove_projects(self):
        self._remove_project_window.set_projects()
        self._remove_project_window.show()

    def remove_project(self, project: str):
        logger.debug(f"remove_project called with {project} in GUI")
        idx = self.config.projects.index(project)
        self.config.remove_project(project)
        self.menu.removeAction(self._project_actions[idx])

    def quit(self):
        logger.info("Exiting")
        self.app.quit()
        self._stop_heartbeats()

    def _stop_heartbeats(self):
        logger.debug("Stopping heartbeats")
        self._is_quitting = True
        if self._hb_thread is not None:
            self._hb_thread.join(timeout=self._pulse_time)
        self._is_quitting = False
        self._hb_thread = None
        logger.debug("Heartbeats stopped")

    @property
    def _pulse_time(self) -> float:
        return self.interval + 1

    @property
    def _commit_interval(self) -> float:
        return max(0.1, self.interval - 1)

    def _send_heartbeats(self):
        with self.client:
            while True:
                heartbeat_data = {"project": self.selected_project}
                now = datetime.now(timezone.utc)
                heartbeat_event = Event(timestamp=now, data=heartbeat_data)

                # Now we can send some events via heartbeats
                # The duration between the heartbeats will be less than pulsetime, so they will get merged.
                logger.debug(f"Sending data: {heartbeat_data}")
                self.client.heartbeat(
                    self.bucket_id,
                    heartbeat_event,
                    pulsetime=self._pulse_time,
                    queued=True,
                    commit_interval=self._commit_interval,
                )

                # Sleep a second until next heartbeat
                sleep(self.interval)

                if self._is_quitting:
                    break

    def _start_heartbeats(self):
        logger.debug("Starting heartbeats")
        self._hb_thread = Thread(target=self._send_heartbeats)
        self._hb_thread.start()

    def _select_project(self, project: str):
        self.selected_project = project
        self._show_selected(project)
        if self._hb_thread is None:
            self._start_heartbeats()
        logger.debug(f"selected project {project}")

    def _show_selected(self, project: str):
        self.tray.setIcon(make_text_icon(project[:3]))
        action: g.QAction
        for action in self.menu.actions():
            if action.text() == project:
                action.setChecked(True)
            else:
                action.setChecked(False)

    def _set_no_project(self):
        logger.debug("Set no project")
        self.selected_project = None
        self._show_selected("N/A")
        self._stop_heartbeats()
