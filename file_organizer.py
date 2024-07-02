from time import sleep

from src.features.file_organizer import file_organizer
from src.features.file_organizer.argument_parser import parse_arguments
from src.utils.rich_console import displayIntro, print_separator

if __name__ == "__main__":
    args = parse_arguments()

    print()
    displayIntro()

    sleep(1.5)

    print_separator("File Organizer")
    file_organizer.main(
        args.input_path,
        output_path=args.output_path,
        verbose=args.verbose,
        file_name_template=args.file_name_template,
        folder_structure=args.folder_structure,
        recursive=args.recursive,
        copy_mode=args.copy,
        auto_clean_output=args.auto_clean_output,
    )
