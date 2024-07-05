import os
from math import ceil
from typing import Literal

import matplotlib.pyplot as plt
from exiftool import ExifToolHelper
from imagehash import ImageHash, average_hash
from PIL import Image
from rich.columns import Columns
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from src.constants.allowed_extensions import IMG_EXTENSIONS
from src.utils.file_date_getters import get_datefile_to_organize
from src.utils.path_utils import filter_filepaths, get_filepaths
from src.utils.rich_console import console, print_log, print_warn, progress_bar


def remove_images(paths_to_remove: list[str], verbose: bool):
    space_saved = 0

    for img in paths_to_remove:
        space_saved += os.path.getsize(img)

        os.remove(img)

        print_log(f"✅ File {os.path.relpath(img, os.getcwd())} removed", verbose)

    console.print(
        f"[green bold][OK]:[/green bold] All images deleted succesfully. You have saved [bold]{round(space_saved / 1000000, 2)}MB[/bold] of space!"
    )


def plot_images(
    paths: list[str], *, fig_title: str = "", verbose: bool, plot_disabled: bool
):
    """Plot a set of images in a new window (only if the user
    has activated the option `plot_before_confirm` in the user_settings.yaml file)."""

    if plot_disabled:
        return

    plt.ioff()

    to_be_plotted = paths

    if len(to_be_plotted) > 16:
        print_warn(
            "For performance reasons, only the first 16 images to be displayed in the window will be shown"
        )

        to_be_plotted = to_be_plotted[:16]

    print_log(
        f"Plotting [bold]{len(to_be_plotted)}[/bold] images...",
        is_verbose=verbose,
        start="\n",
    )

    figure = plt.figure(
        fig_title + (f" (Showing 16 of {len(paths)})" if len(paths) > 16 else "")
    )

    NUMBER_OF_COLS = ceil(len(to_be_plotted) / 3.5)
    NUMBER_OF_ROWS = ceil(len(to_be_plotted) / NUMBER_OF_COLS)

    for i, img in enumerate(to_be_plotted):
        to_plot = figure.add_subplot(NUMBER_OF_COLS, NUMBER_OF_ROWS, i + 1)
        to_plot.set_xticks([])
        to_plot.set_yticks([])
        to_plot.set_xlabel(f"Image [{i}]")
        to_plot.imshow(plt.imread(img))

    PADDING = 0.075
    plt.subplots_adjust(
        left=PADDING,
        right=1 - PADDING,
        top=1 - PADDING,
        bottom=PADDING,
        hspace=0.4,
        wspace=0.1,
    )

    plt.show(block=False)


def find_file_to_keep(
    files: list[str],
    order_method: Literal["size"] | Literal["date"],
    et: ExifToolHelper,
):
    """Finds the file to keep in a list of duplicates/similar files"""

    files = list(filter(lambda x: os.path.exists(x) and os.path.isfile(x), files))

    if order_method == "size":
        files.sort(
            key=lambda x: os.path.getsize(x),
            reverse=True,
        )

    if order_method == "date":
        files.sort(
            key=lambda x: get_datefile_to_organize(filepath=x, et=et), reverse=True
        )

    return files[0]


def main(
    input_path: str,
    hash_size: int,
    similarity: int,
    recursive: bool,
    verbose: bool,
    plot_disabled: bool,
):
    """Optionally find and remove duplicate images"""

    console.print(
        f"[blue bold][INFO]:[/blue bold] Preparing the search for similar images with the following parameters:\n"
    )

    console.print(f"\t[blue]-[/blue] Similarity: [bold]{similarity}%[/bold]")
    console.print(f"\t[blue]-[/blue] Hash size: [bold]{hash_size}[/bold]")

    print()

    filepaths = filter_filepaths(
        get_filepaths(input_path, recursive),
        allowed_ext=set(IMG_EXTENSIONS),
    )

    duplicates_imgs: list[tuple[list[str], float]] = []

    files_and_hashes: list[tuple[str, ImageHash]] = []

    with progress_bar() as p:
        for path, filename in p.track(filepaths, description="Finding duplicates:"):
            full_path_to_file = os.path.join(path, filename)

            try:
                img = Image.open(full_path_to_file)
            except:
                continue

            if not img:
                continue

            with img:
                try:
                    temp_hash = average_hash(img, hash_size)

                    if temp_hash:
                        files_and_hashes.append((full_path_to_file, temp_hash))
                except:
                    continue

    threshold = 1 - similarity / 100
    diff_limit = int(threshold * (hash_size**2))

    print()

    for i, file1 in enumerate(files_and_hashes):
        duplicates: list[str] = []
        _similarity: float

        for file2 in files_and_hashes[i:]:
            if file1[0] != file2[0]:
                if file1[1] - file2[1] < diff_limit:
                    if len(duplicates) == 0:
                        duplicates.append(file1[0])

                    duplicates.append(file2[0])
                    _similarity = round(100 * ((file1[1] - file2[1]) / hash_size**2), 2)

        already_found = False
        for founded in duplicates_imgs:
            if set(duplicates) <= set(founded[0]):
                already_found = True

        if len(duplicates) > 0 and not already_found:
            duplicates_imgs.append((duplicates, _similarity))

    console.print(
        f"[green bold][OK]:[/green bold] Duplicate search finished with success.\n"
    )

    if len(duplicates_imgs) == 0:
        console.print(
            "[green bold][INFO]:[/green bold] No duplicates found. Nothing more to do in this step"
        )
        return

    console.print(
        f"[blue bold][INFO]:[/blue bold] Some similar images has been found:\n"
    )

    columns_panels_to_print: list[str] = []

    for duplication_group_info in duplicates_imgs:
        text_to_append = f"Similarity: {100 - duplication_group_info[1]}%:\n\n"
        for img in duplication_group_info[0]:
            text_to_append += f"[blue]-[/blue] {os.path.relpath(img, os.getcwd())}\n"

        columns_panels_to_print.append(text_to_append)

    console.print(
        Columns([Panel(panel, expand=True) for panel in columns_panels_to_print])
    )

    print()

    console.print(
        "Now you have choose the action that we should apply to this similar images. You have [bold]3[/bold] options:\n",
        "\n\t[0] - Do nothing with my images, I'm good with the similarities.",
        "\n\t[1] - Keep the biggest image on each group and remove the rest",
        "\n\t[2] - Keep the most recent image on each group and remove the rest",
        "\n\t[3] - Let me choose what files to keep in each group",
        "\n\t[4] - Let me choose what files to remove in each group",
    )

    action_selection = Prompt.ask(
        "\nChoose an option", choices=["0", "1", "2", "3", "4"]
    )

    if action_selection == "0":
        console.print(
            "\n[bold blue][INFO]:[/bold blue] The duplicates remover will not make any action"
        )
        return

    if action_selection == "1" or action_selection == "2":
        paths_to_remove: list[str] = []

        with ExifToolHelper() as et:
            for duplication_group_info in duplicates_imgs:
                IMG_TO_REMOVE = find_file_to_keep(
                    duplication_group_info[0],
                    "date" if action_selection == "2" else "size",
                    et,
                )

                duplication_group_info[0].remove(IMG_TO_REMOVE)

                for img in duplication_group_info[0]:
                    if os.path.exists(img) and os.path.isfile(img):
                        paths_to_remove.append(img)

        paths_to_remove = list(
            set(paths_to_remove)
        )  # Remove duplicates files from the list to be removed

        plot_images(
            paths_to_remove,
            fig_title="Images to be removed",
            verbose=verbose,
            plot_disabled=plot_disabled,
        )

        confirm_remove = Confirm.ask(
            f"\nThis action will delete [bold]{len(paths_to_remove)}[/bold] images from the output directory. Are you sure?",
            default=False,
        )

        if not plot_disabled:
            plt.close()

        if confirm_remove is True:
            remove_images(paths_to_remove=paths_to_remove, verbose=verbose)

        else:
            console.print(
                "\n[blue bold][INFO]:[/blue bold] Operation cancelled. No images have been removed"
            )

    elif action_selection == "3" or action_selection == "4":
        for index, duplication_group_info in enumerate(duplicates_imgs):
            # For each group of duplicates:

            images_in_group = duplication_group_info[0]

            plot_images(
                paths=images_in_group,
                fig_title=f"Group {index + 1}/{len(duplicates_imgs)}",
                verbose=verbose,
                plot_disabled=plot_disabled,
            )

            console.print(
                f"\n[bold]Group {index}[/bold] [i](similarity: {100 - duplication_group_info[1]}%)[/i]:"
            )

            img_text: str = ""

            for i, img in enumerate(images_in_group):
                img_text += (
                    f"\n\t[{i}] - {os.path.relpath(img, os.getcwd())}"
                    f" - [i]{round(os.path.getsize(img) / 1000000, 2)}MB[/i]"
                )

            console.print(img_text)

            images_selected: list[int] = []

            while True:
                ACTION_TEXT = "keep" if (action_selection == "3") else "delete"

                response = Prompt.ask(
                    f"\nSelect images to {ACTION_TEXT}. "
                    f"Type the number of images separated by commas or press Intro to {ACTION_TEXT} all the images"
                )

                if response == "":
                    break

                try:
                    images_selected = list(
                        map(lambda x: int(x), response.replace(" ", "").split(","))
                    )
                except Exception:
                    console.print(f"\n[red] Please type only valid numbers")
                    continue

                if set(images_selected).issubset(range(len(images_in_group))):
                    break
                else:
                    console.print(f"\n[red] A selected index in not a valid option")

            console.print(
                f"\n[blue bold][INFO]:[/blue bold] {len(images_selected)} image(s) have been selected"
            )

            paths_to_remove: list[str] = []

            if action_selection == "4":
                # Remove the selected indexes
                paths_to_remove = list(
                    set([images_in_group[i] for i in images_selected])
                )
            elif action_selection == "3":
                # Remove the NOT selected indexes
                paths_to_remove = list(
                    set(
                        [
                            images_in_group[i]
                            for i in range(len(images_in_group))
                            if i not in images_selected
                        ]
                    )
                )

            if len(paths_to_remove) == 0:
                console.print(
                    f"\n[blue bold][INFO]:[/blue bold] No images to be removed. Nothing to do with this group!"
                )

                if not plot_disabled:
                    plt.close()

                continue

            console.print(
                f"\n[blue bold][INFO]:[/blue bold] Number of images to be removed: {len(paths_to_remove)}\n"
            )

            remove_images(paths_to_remove=paths_to_remove, verbose=verbose)

            if not plot_disabled:
                plt.close()
