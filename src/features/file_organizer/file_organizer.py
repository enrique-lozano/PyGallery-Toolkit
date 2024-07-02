import filecmp
import os
import re
import shutil
from datetime import datetime
from typing import Any, List

import exiftool
from exiftool import ExifToolHelper

from src.constants.user_settings import USER_SETTINGS
from src.features.file_organizer.key_directives import (
    custom_app_directives,
    python_date_directives,
)
from src.utils import rich_console
from src.utils.check_input_path import check_input_path
from src.utils.confirm import confirm_question
from src.utils.file_date_getters import get_datefile_to_organize
from src.utils.path_utils import get_filepaths
from src.utils.rich_console import (
    console,
    print_error,
    print_log,
    print_warn,
    progress_bar,
)


def get_metadata_str(metadata: dict[str, Any], keys: list[str]):
    for key in keys:
        if metadata.get(key):
            return str(metadata.get(key))

    return "Unknown"


def replace_attr_variables(part: str, filepath: str, et: ExifToolHelper):
    custom_attr = re.findall("(%[a-zA-Z_]+)", part)

    if set(custom_attr) <= set(python_date_directives):
        filedate = get_datefile_to_organize(filepath, et)
        part = datetime.strftime(filedate, part)

    else:
        for directive in custom_attr:
            if directive in python_date_directives:
                filedate = get_datefile_to_organize(filepath, et)

                part = part.replace(directive, datetime.strftime(filedate, directive))

            elif directive in custom_app_directives:
                metadata: dict[str, Any] = et.get_metadata(filepath)[0]

                if "software" in directive:
                    part = part.replace(
                        directive, get_metadata_str(metadata, ["EXIF:Software"])
                    )

                if "camera_maker" in directive:
                    part = part.replace(
                        directive,
                        get_metadata_str(metadata, ["EXIF:Make", "QuickTime:Make"]),
                    )

                if "camera_model" in directive:
                    part = part.replace(
                        directive,
                        get_metadata_str(metadata, ["EXIF:Model", "QuickTime:Model"]),
                    )

            else:
                raise Exception(f"Custom directive not accepted: {directive}")

    return part


def get_folder_path(folder_structure: list[str], filepath: str, et: ExifToolHelper):
    to_return: list[str] = []

    for part in folder_structure:
        to_return.append(replace_attr_variables(part, filepath, et))

    return to_return


def get_file_location(
    _folder_structure: list[str], output_path: str, filepath: str, et: ExifToolHelper
):
    path_destination: str = ""

    folder_structure = get_folder_path(_folder_structure, filepath, et)

    path_destination = os.path.join(*([output_path] + folder_structure))

    if path_destination == "":
        return "Unknown"

    if not os.path.exists(path_destination):
        os.makedirs(path_destination)

    return path_destination


def get_new_file_name(filepath: str, et: ExifToolHelper):
    template: str | None = USER_SETTINGS.get("file_organizer").get("file_name_template")  # type: ignore

    if template == "" or template is None:
        return os.path.basename(filepath)

    base, extension = os.path.splitext(filepath)

    return f"{replace_attr_variables(template, filepath, et)}{extension}"


def make_unique_filename(new_filepath: str, current_filepath: str):
    duplicate_nr = 0
    base, extension = os.path.splitext(new_filepath)

    if new_filepath == current_filepath and filecmp.cmp(new_filepath, current_filepath):
        # Same file in same dir -> No need to move
        return None

    while os.path.exists(new_filepath):
        duplicate_nr += 1
        new_filepath = f"{base} ({duplicate_nr}){extension}"

    return new_filepath


def main(
    input_path: str,
    *,
    output_path: str | None,
    recursive: bool,
    auto_clean_output: bool,
    verbose: bool,
    folder_structure: str,
    file_name_template: str | None,
    copy_mode: bool,
):
    check_input_path(input_path)

    print()

    if folder_structure.strip() == "":
        print_error(
            "Validation error: [i]folder_structure[/i]",
            descr="The [i]folder_structure[/i]argument can not be empty",
        )

    if output_path is None:
        default_path = os.path.join(os.getcwd(), "output")
        output_path = rich_console.console.input(
            f"You have not specified the output directory. Please specify one or press Enter to use the default one [grey62]({default_path})[/grey62]: ",
        )

        if output_path is None or output_path.strip() == "":
            output_path = default_path

    print()

    # Creating output directory if not exists
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        rich_console.console.print(
            "[blue bold][INFO]:[/blue bold] Output directory not found. A new one has been created"
        )

    # Check if output directory has some content already
    elif len(os.listdir(output_path)) > 0:
        if auto_clean_output:
            print_warn(
                "You have some files/directories in the specified output directory. Any content here will be removed and replaced by the new data. To change this behavior, run the script without the [i]auto_clean_output[/i] argument"
            )

        confirm_remove = auto_clean_output or confirm_question(
            f"You have content in the specified output directory. To start and fill this directory, this script require the output directory to be clean. We can delete all the content in this directory now if you want. Continue?",
            default=False,
        )

        if not confirm_remove:
            print_error(
                "The program require the output directory to be clean",
                descr="Remove all the content in the output directory or specify a new one and re-run the script.",
            )

        for filename in os.listdir(output_path):
            file_path = os.path.join(output_path, filename)

            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print("Failed to delete %s. Reason: %s" % (file_path, e))

        print()

    # ------------------------------------------------- #
    # ----------- MAIN EXECUTION PROCCESS ------------- #
    # ------------------------------------------------- #

    filepaths = get_filepaths(input_path, recursive)

    if len(filepaths) == 0:
        console.print(
            f"[green bold][OK]:[/green bold] Ops! We can not find files to organize in your input directory. Program finish with success.\n"
        )
        return

    with exiftool.ExifToolHelper() as et:
        with progress_bar() as p:
            for path, filename in p.track(
                filepaths, description="Organizing your library:"
            ):
                filepath = os.path.join(path, filename)

                new_file_location = os.path.join(
                    get_file_location(
                        folder_structure.split("/"), output_path, filepath, et
                    ),
                    get_new_file_name(filepath, et),
                )

                new_file_location = os.path.abspath(new_file_location)
                new_file_location = make_unique_filename(new_file_location, filepath)

                if new_file_location is not None:
                    paths_to_log = (
                        os.path.relpath(filepath, input_path),
                        os.path.relpath(new_file_location, output_path),
                    )

                    if copy_mode:
                        shutil.copy2(filepath, new_file_location)
                        print_log(
                            f"✅ File {paths_to_log[0]} copied to {paths_to_log[1]}",
                            verbose,
                        )
                    else:
                        shutil.move(filepath, new_file_location)
                        print_log(
                            f"✅ File {paths_to_log[0]} moved to {paths_to_log[1]}",
                            verbose,
                        )
