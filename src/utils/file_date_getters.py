import os
import re
from datetime import datetime
from typing import Any, Literal

from exiftool import ExifToolHelper

from src.constants.datetaken_templates import (
    DATE_PATTERNS_TO_FORMATS,
    FILENAME_DATE_MAX,
    FILENAME_DATE_MIN,
)


def get_datetime_from_filename(filename: str) -> datetime | None:
    """
    Get the datetime of the file based on its name using dynamic pattern matching.

    This function uses regular expressions to match potential date parts in the filename.
    It attempts to parse these parts using a set of predefined datetime formats.
    The map of date patterns to formats is sorted from more specific to less specific
    to ensure that more detailed formats (including minutes and seconds) are attempted first.

    Args:
        filename (str): The name of the file to extract the datetime from.

    Returns:
        datetime: The extracted datetime object if a valid date is found within the defined range, else None.
    """
    date_to_return = None

    for pattern, date_format in DATE_PATTERNS_TO_FORMATS.items():
        match = re.search(pattern, filename)
        if match:
            date_str = match.group()
            try:
                date_to_return = datetime.strptime(date_str, date_format)
                # Check if the year is within the valid range
                if FILENAME_DATE_MIN <= date_to_return.year <= FILENAME_DATE_MAX:
                    return date_to_return
            except ValueError:
                continue

    return None


def get_date_from_os(filepath: str):
    return min(
        datetime.fromtimestamp(os.path.getctime(filepath)),
        datetime.fromtimestamp(os.path.getmtime(filepath)),
    )


def get_date_from_exif(filepath: str, et: ExifToolHelper):
    """Get the datetime of the file based on its metadata."""

    metadata: dict[str, Any] = et.get_metadata(filepath)[0]

    # print(json.dumps(str(metadata)))

    keys = [
        "EXIF:DateTimeOriginal",
        "XMP:DateTimeOriginal",
        "QuickTime:CreateDate",
        "EXIF:CreateDate",
        "EXIF:ModifyDate",
    ]

    for key in keys:
        if metadata.get(key):
            return datetime.strptime(
                str(metadata.get(key)),
                "%Y:%m:%d %H:%M:%S",
            )


def get_filedate(
    way: Literal["filename"] | Literal["filedate"] | Literal["fileexif"],
    filename: str,
    filepath: str,
    et: ExifToolHelper,
):
    if way == "filename":
        return get_datetime_from_filename(filename)

    elif way == "filedate":
        return get_date_from_os(filepath)

    else:
        return get_date_from_exif(filepath, et)


def get_datefile_to_organize(filepath: str, et: ExifToolHelper):
    """Get the datetime of the file based on its metadata. If we can not found the date in file metadata, the file OS date will be used"""

    try:
        to_return = get_date_from_exif(filepath, et)

    except:
        return get_date_from_os(filepath)

    if not to_return:
        to_return = get_date_from_os(filepath)

    return to_return
