import os

from src.utils.rich_console import print_error


def check_input_path(path: str):
    if not os.path.exists(path):
        print_error(
            title="The input path specified does not exist.",
            descr=f"Modify your config file or create a folder called {path} in this directory and add some photos to start.",
        )

    if not os.path.isdir(path):
        print_error(
            title="The input path specified is not a directory",
            descr=f"Modify your config file or create a folder called {path} in this directory and add some photos to start.",
        )
