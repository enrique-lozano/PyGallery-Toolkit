from src.utils import rich_console


def confirm_question(msg: str, *, default: bool | None = False) -> bool:
    while True:
        default_style = "grey74 bold"
        yOrN = (
            "y/n"
            if default is None
            else (
                f"[{default_style}]Y[/{default_style}]/n"
                if default
                else f"y/[{default_style}]N[/{default_style}]"
            )
        )

        value = rich_console.console.input(
            msg + f" [grey62]({yOrN})[/grey62]: "
        ).lower()

        if value in ("y", "yes"):
            rv = True
        elif value in ("n", "no"):
            rv = False
        elif default is not None and value == "":
            rv = default
        else:
            rich_console.print_error(
                "Invalid input. Please type y or n", finishExecution=False
            )
            continue
        break

    return rv
