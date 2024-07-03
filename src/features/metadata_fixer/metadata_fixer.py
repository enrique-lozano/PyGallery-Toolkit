import os
from datetime import datetime
from typing import Any, Literal

import exiftool
from rich.table import Table

from src.utils.check_input_path import check_input_path
from src.utils.file_date_getters import (
    get_date_from_exif,
    get_date_from_os,
    get_filedate,
)
from src.utils.path_utils import get_filepaths
from src.utils.rich_console import console, print_log, progress_bar


def get_exif_datestr(datetime: datetime):
    return datetime.strftime("%Y:%m:%d %H:%M:%S")


FileStatus = Literal["updated"] | Literal["skipped"] | Literal["error"]


def metadata_fixer(
    input_path: str,
    *,
    recursive: bool,
    verbose: bool,
    overwrite_dates: bool,
    os_dates: bool,
    gps_fix: bool,
    dates_from: list[Literal["filename"] | Literal["filedate"] | Literal["fileexif"]],
):
    check_input_path(input_path)

    filepaths = get_filepaths(input_path, recursive)

    console.print(
        f"[blue bold][INFO]:[/blue bold] Starting the metadata-fixer with the force mode {'enabled' if overwrite_dates else 'disabled'}.\n"
    )

    results: list[FileStatus] = []

    def log_error(title: str):
        print_log(f"❌ {title}", True)
        results.append("error")

    with exiftool.ExifToolHelper() as et:
        with progress_bar() as p:
            for path, filename in p.track(filepaths, description="Fixing metadata:"):
                filepath = os.path.join(path, filename)

                file_status: FileStatus = "skipped"

                try:
                    metadata: dict[str, Any] = et.get_metadata(filepath)[0]

                except UnicodeEncodeError:
                    log_error(
                        f"File {filename} -> Error while trying to read the file metadata. [UnicodeEncodeError]"
                    )

                    continue

                except:
                    log_error(
                        f"File {filename} -> Error while trying to read the file metadata"
                    )

                    continue

                # ------------------------------------------------- #
                # ------------- DATETIME EXIF FIXER --------------- #
                # ------------------------------------------------- #

                """ We should edit the dates if the force mode is enabled or if no DateTimeOriginal tag is in the metadata"""
                shouldEditDates = (
                    overwrite_dates
                    or sum(
                        1
                        for key in metadata.keys()
                        if len(key.split(":")) > 1
                        and key.split(":")[1] == "DateTimeOriginal"
                    )
                    == 0
                )

                if shouldEditDates:
                    file_datetime: datetime | None = None

                    for datimegetter in dates_from:
                        # Get the filedate based on the user settings
                        if file_datetime is None:
                            try:
                                file_datetime = get_filedate(
                                    datimegetter, filename, filepath, et
                                )
                            except:
                                log_error(
                                    f"File {filename} -> Error while trying to getting the datetime of this item"
                                )
                                continue

                    if file_datetime:
                        try:
                            et.set_tags(
                                filepath,
                                {
                                    "DateTimeOriginal": get_exif_datestr(file_datetime),
                                    "CreateDate": get_exif_datestr(file_datetime),
                                },
                                params=["-overwrite_original"],
                            )

                            print_log(
                                f"✅ File {filename} -> DateTime metadata updated to {file_datetime}",
                                verbose,
                            )

                            file_status = "updated"

                        except:
                            log_error(
                                f"File {filename} -> Error while trying to update the datetime"
                            )
                            continue

                    else:
                        print_log(
                            f"⏩ File {filename} -> Skipped (date can not be found)",
                            verbose,
                        )

                else:
                    print_log(
                        f"⏩ File {filename} -> Skipped (dateTimeOriginal already in metadata)",
                        verbose,
                    )

                # ------------------------------------------------- #
                # ---------------- GPS EXIF FIXER ----------------- #
                # ------------------------------------------------- #

                if (
                    gps_fix is True
                    and metadata.get("Composite:GPSPosition") is not None
                    and sum(
                        1
                        for key in metadata.keys()
                        if len(key.split(":")) > 0 and key.split(":")[0] == "QuickTime"
                    )
                    > 0
                    and metadata.get("QuickTime:GPSCoordinates") is None
                ):
                    gps_position = str(metadata.get("Composite:GPSPosition")).split(" ")
                    new_latitude = round(float(gps_position[0]), 4)
                    new_longitude = round(float(gps_position[1]), 4)

                    # print(gps_position, new_latitude, new_longitude)

                    try:
                        et.set_tags(
                            filepath,
                            {
                                "QuickTime:GPSCoordinates": " ".join(
                                    [
                                        str(new_latitude),
                                        str(new_longitude),
                                    ]
                                ),
                            },
                            params=["-overwrite_original"],
                        )

                        print_log(
                            f"✅ File {filename} -> GPS metadata updated",
                            verbose,
                        )

                        file_status = "updated"

                    except:
                        log_error(
                            f"File {filename} -> Error while trying to update the GPS data"
                        )
                        continue

                # ------------------------------------------------- #
                # ---------------- OS DATES FIXER ----------------- #
                # ------------------------------------------------- #

                if os_dates:
                    try:
                        date_to_set = get_date_from_exif(filepath, et)

                        if (
                            date_to_set is not None
                            and get_date_from_os(filepath) != date_to_set
                        ):
                            et.set_tags(
                                filepath,
                                {
                                    "filemodifydate": date_to_set,
                                    "filecreatedate": date_to_set,
                                },
                                params=["-overwrite_original"],
                            )

                            print_log(
                                f"✅ File {filename} -> File creation/modify date updated to {date_to_set}",
                                verbose,
                            )

                            file_status = "updated"
                    except:
                        log_error(
                            f"File {filename} -> File date created/modify can not be set"
                        )
                        file_status = "error"

                results.append(file_status)

    console.print(
        "[green bold][OK]:[/green bold] All files have been successfully processed!\n"
    )

    # ---- PRINT THE RESULTS ---- #

    table = Table(
        title="Results",
        show_header=False,
        show_lines=True,
        title_justify="left",
    )

    table.add_column(no_wrap=True)
    table.add_column(justify="right", style="bold")

    table.add_row(
        "✅ Files with new/updated metadata",
        f"{results.count('updated')}",
    )
    table.add_row("⏩ Files skipped", f"{results.count('skipped')}")
    table.add_row("❌ Files with error", f"{results.count('error')}")

    console.print(table)
