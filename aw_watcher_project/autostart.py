import os
import platform
import shutil
from pathlib import Path

import typer

from aw_watcher_project.config import ASSETS_PATH
from aw_watcher_project.logger import logger

LINUX_CONFIG_DIRECTORY = Path("~").expanduser() / ".config" / "autostart"
LINUX_DESKTOP_FILE_NAME = "aw-watcher-project.desktop"
LINUX_AUTOSTART_FILE = ASSETS_PATH / LINUX_DESKTOP_FILE_NAME
LINUX_OUT_FILE = LINUX_CONFIG_DIRECTORY / LINUX_DESKTOP_FILE_NAME

app = typer.Typer(help='Control system auto-start behavior')


def check_os() -> str:
    os_name = platform.system()
    if os_name in ("Darwin", "Windows"):
        raise NotImplementedError(
            f"no support for automatically enabling autostart in OS {os_name}. "
            f"Please manually add aw-watcher-project to startup applications"
        )
    return os_name


def _bootstrap_autostart_linux():
    if not LINUX_CONFIG_DIRECTORY.exists():
        raise NotImplementedError(
            f"Must have {LINUX_CONFIG_DIRECTORY} for autostart bootstrap to work on Linux. "
            f"Please manually add aw-watcher-project to startup applications"
        )
    shutil.copy(LINUX_AUTOSTART_FILE, LINUX_OUT_FILE)
    logger.info(
        f"Copied autostart file to {LINUX_OUT_FILE}. Will autostart on next login"
    )


def _remove_autostart_linux():
    if LINUX_OUT_FILE.exists():
        os.remove(LINUX_OUT_FILE)
        logger.info(f"Removed autostart file {LINUX_OUT_FILE}. Autostart disabled")
    else:
        logger.info("No autostart file exists. No action taken.")


@app.command(name="bootstrap")
def bootstrap_autostart():
    """
    Bootstraps auto-start behavior so app will start
    automatically from next log in
    """
    os_name = check_os()
    if os_name == "Linux":
        _bootstrap_autostart_linux()
    # TODO: implement Windows and Mac autostart bootstrap


@app.command(name="remove")
def remove_autostart():
    """
    Removes auto-start behavior
    """
    os_name = check_os()
    if os_name == "Linux":
        _remove_autostart_linux()
    # TODO: implement Windows and Mac remove autostart


if __name__ == "__main__":
    app()
