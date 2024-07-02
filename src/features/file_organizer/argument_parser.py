import argparse
from typing import List

from src.utils.add_common_args import add_common_args


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Organize photos and videos based on their metadata",
        add_help=True,
        exit_on_error=True,
    )

    parser.add_argument(
        "-o",
        "--output_path",
        type=str,
        help="Absolute path to save the proccessed images. If it is the same as the input_path the images will be overwritten in that same directory",
    )

    parser.add_argument(
        "--folder_structure",
        type=str,
        default="%Y/%m - %B",
        help="Folder tree in which your files will be organized based on their metadata. Each list element will be a level in the new folder structure. To separate by subdirectories, just use a forward slash (even if you are on Windows). Defaults to '%Y/%m - %B'",
    )

    parser.add_argument(
        "--file_name_template",
        type=str,
        help="""
        Names that will have the parsed files in the output directory. Leave it blank or null if you want the current file name to be maintained.
        
        Be careful when specifying this attribute, since a template that is too generic could lead to many duplicates. When this happens, file names are created by adding (1), (2)... to the current name""",
    )

    parser.add_argument(
        "--auto_clean_output",
        action="store_true",
        default=False,
        help="Wheter we should reset the output directory before start. If `false` we will ask the user before remove any content in the output directory",
    )

    parser.add_argument(
        "-c",
        "--copy",
        action="store_true",
        default=False,
        help="Copy files instead of moving",
    )

    add_common_args(parser)

    return parser.parse_args()
