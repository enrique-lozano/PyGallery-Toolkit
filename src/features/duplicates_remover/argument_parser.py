import argparse

from src.utils.add_common_args import add_common_args


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Remove duplicates/similar images",
        add_help=True,
        exit_on_error=True,
    )

    parser.add_argument(
        "--hash_size",
        default=16,
        type=int,
        help="Used for identification of similar images. With larger values the search will be more exhaustive but slower. Giving a value of 0 skips the search for duplicates/similar altogether",
    )

    parser.add_argument(
        "-s",
        "--similarity",
        type=int,
        default=96,
        help="Similarity of the images that will trigger an action (the action will be chosen by the user). It is a number from 0 to 100, with 100 being the number to pass when we want only completely identical images to appear. This parameter does not affect the speed of the process, as does `hash_size`",
    )

    parser.add_argument(
        "--plot_disabled",
        default=False,
        action="store_true",
        help="Display the images before confirm the removal",
    )

    add_common_args(parser)

    return parser.parse_args()
