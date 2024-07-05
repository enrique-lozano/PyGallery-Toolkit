from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

console = Console(highlight=False)
__err_console = Console(stderr=True, log_time=False, log_path=False)


def progress_bar():
    return Progress(
        TextColumn("{task.description}"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        BarColumn(
            style="white", complete_style="green bold", finished_style="green bold"
        ),
        MofNCompleteColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
        # TextColumn("•"),
        # TimeRemainingColumn(),
        TextColumn("\n"),
        console=console,
    )


def displayIntro():
    console.print(
        Panel.fit(
            "Created with ❤ by [link=https://github.com/enrique-lozano]Enrique Lozano[/] and maintened by the Open Source community.",
            box=box.ROUNDED,
            padding=(1, 2),
            title="[b blue]Thanks for trying out PyGallery!",
            border_style="bright_blue",
        ),
        justify="center",
    )


def print_separator(title: str):
    """
    Print a decorative separator with a title.

    Parameters:
    title (str): The title to be displayed within the separator.

    Returns:
    None
    """
    print()
    console.rule(f"[bold dark_green on white]  {title}  ")
    print()


def print_warn(title: str):
    """
    Print a warning message in a specific format.

    Parameters:
    title (str): The warning message to be displayed.

    Returns:
    None
    """
    console.print(f"\n[orange1 bold][WARN]:[/orange1 bold][navajo_white1] {title}")


def print_log(msg: str, is_verbose: bool, *, start=""):
    """
    Print a log message if verbose mode is enabled.

    Parameters:
    msg (str): The log message to be displayed.
    is_verbose (bool): A flag to determine if the log message should be printed.
    start (str): An optional prefix to the log message. Defaults to an empty string.

    Returns:
    None
    """
    if is_verbose is True:
        console.print(f"{start}[light_steel_blue][LOG]:[/light_steel_blue] {msg}")


def print_error(title: str, *, descr: str | None = None, finishExecution: bool = True):
    print()
    __err_console.log(f"[red bold][ERROR]: [/red bold][red]{title}")
    print()

    if descr is not None:
        __err_console.print(f"[#FFB5B5 italic]{descr}")

    if finishExecution:
        quit(1)
    else:
        print()
