from time import sleep

from src.features.metadata_fixer import metadata_fixer
from src.features.metadata_fixer.argument_parser import parse_arguments
from src.utils.rich_console import displayIntro, print_separator

if __name__ == "__main__":
    args = parse_arguments()

    print()
    displayIntro()

    sleep(1.5)

    print_separator("Metadata fixer")
    metadata_fixer.metadata_fixer(
        args.input_path,
        verbose=args.verbose,
        overwrite_dates=args.overwrite_dates,
        gps_fix=args.gps_fix,
        os_dates=args.os_dates,
        recursive=args.recursive,
        dates_from=args.dates_from,
    )
