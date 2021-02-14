import typer

from aw_watcher_project import autostart
from aw_watcher_project.app import ProjectWatcherApp

app = typer.Typer()
app.add_typer(autostart.app, name="autostart")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Run command without arguments to start the system tray GUI.
    Use the autostart subcommand to bootstrap or remove auto-start behavior
    """
    if ctx.invoked_subcommand is None:
        # Ran without arguments, start GUI
        ProjectWatcherApp()


if __name__ == "__main__":
    app()
