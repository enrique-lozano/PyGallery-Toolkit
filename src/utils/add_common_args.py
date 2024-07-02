import argparse
from argparse import ArgumentParser


def add_common_args(parser: ArgumentParser):
    parser.add_argument(
        "input_path", type=str, help="Absolute path to the images to proccess"
    )

    parser.add_argument(
        "--recursive",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Wheter we should search for files in subdirectories of the input directory",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose output",
    )
