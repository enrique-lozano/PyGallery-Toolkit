from datetime import datetime

# Map of regex patterns to corresponding datetime formats, sorted from more specific to less specific. To check the possible options to parse, check the table here https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
DATE_PATTERNS_TO_FORMATS = {
    r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}": "%Y-%m-%d %H:%M:%S",  # YYYY-MM-DD HH:MM:SS
    r"\d{4}-\d{2}-\d{2} \d{2}.\d{2}.\d{2}": "%Y-%m-%d %H.%M.%S",  # YYYY-MM-DD HH.MM.SS
    r"\d{4}-\d{2}-\d{2} at \d{2}.\d{2}.\d{2}": "%Y-%m-%d at %H.%M.%S",  # WhatsApp Image YYYY-MM-DD at HH.MM.SS
    r"\d{8}_\d{6}": "%Y%m%d_%H%M%S",  # YYYYMMDD_HHMMSS
    r"\d{8}-\d{6}": "%Y%m%d-%H%M%S",  # YYYYMMDD-HHMMSS
    r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}": "%Y-%m-%d %H:%M",  # YYYY-MM-DD HH:MM
    r"\d{4}-\d{2}-\d{2} \d{2}.\d{2}": "%Y-%m-%d %H.%M",  # YYYY-MM-DD HH.MM
    r"\d{4}-\d{2}-\d{2}": "%Y-%m-%d",  # YYYY-MM-DD
    r"\d{8}": "%Y%m%d",  # YYYYMMDD
}

FILENAME_DATE_MIN = 1820
FILENAME_DATE_MAX = datetime.now().year + 5
