# UPDATEME With subcommand apps in `cli/commands/`, see documentation at:
# https://typer.tiangolo.com/tutorial/
# See recommended configuration for multicommand applications at:
# https://typer.tiangolo.com/tutorial/one-file-per-command/#main-module-mainpy
from typing import Annotated

import typer
from rich.console import Console

from python_project import __version__
from python_project.cli.styles import AppCustomStyles
from python_project.tui.main_window import TerminalApp

app = typer.Typer()


def version_callback(print_version: bool):
    if print_version:
        Console(theme=AppCustomStyles.NOCTIS).print(
            ":package:[declaration]Python Project[/] "
            f"[bold fstring]{__version__}[/]"
        )

        raise typer.Exit


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,

    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help="Print the current version of this program and exit.",
            callback=version_callback,
            is_eager=True,
        )
    ] = False,
):
    """Launch the Python Project interface."""
    if ctx.invoked_subcommand is None:
        interface = TerminalApp()
        interface.run()
