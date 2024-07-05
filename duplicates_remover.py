from time import sleep

from matplotlib.pyplot import plot

from src.features.duplicates_remover import duplicates_remover
from src.features.duplicates_remover.argument_parser import parse_arguments
from src.utils.rich_console import displayIntro, print_separator

if __name__ == "__main__":
    args = parse_arguments()

    print()
    displayIntro()

    sleep(1.5)

    print_separator("Metadata fixer")
    duplicates_remover.main(
        args.input_path,
        verbose=args.verbose,
        recursive=args.recursive,
        hash_size=args.hash_size,
        similarity=args.similarity,
        plot_disabled=args.plot_disabled,
    )
