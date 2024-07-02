import os


def get_filepaths(path: str, recursive: bool):
    """
    Retrieve a list of file paths from the specified directory.

    Args:
        path (str): The directory path to search for files.
        recursive (bool): If True, search for files recursively in all subdirectories.
                          If False, search only in the specified directory.

    Returns:
        List[Tuple[str, str]]: A list of tuples where each tuple contains the absolute path
                               to the directory and the file name.
    """

    all_filepaths: list[tuple[str, str]] = []

    if not recursive:
        all_filepaths += [
            (path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))
        ]

    else:
        for dirpath, dirnames, filenames in os.walk(path):
            abspath = os.path.abspath(dirpath)
            all_filepaths += [(abspath, f) for f in filenames]

    return all_filepaths


def filter_filepaths(filepaths: list[tuple[str, str]], allowed_ext: set[str]):
    """
    Filter file paths based on allowed file extensions.

    Args:
        filepaths (List[Tuple[str, str]]): A list of tuples where each tuple contains the
                                           absolute path to the directory and the file name.
        allowed_ext (Set[str]): A set of allowed file extensions (e.g., {'.txt', '.jpg'}).

    Returns:
        List[Tuple[str, str]]: A list of tuples containing only the file paths with the allowed extensions.
    """
    return [
        (fp, fn)
        for fp, fn in filepaths
        if os.path.splitext(fn)[-1].lower() in allowed_ext
    ]


""" 
def main(
    input_path: str,
    output_path: str,
    force_datetime_fix: bool,
    hash_size: int,
    similarity: int,
    folder_structure: list[str],
):
    if not os.path.exists(input_path):
        print_error(
            title="The input path specified does not exist.",
            descr=f"Modify your config file or create a folder called {input_path} in this directory and add some photos to start.",
        )

    if not os.path.isdir(input_path):
        print_error(
            title="The input path specified is not a directory",
            descr=f"Modify your config file or create a folder called {input_path} in this directory and add some photos to start.",
        )

    print()

    # Creating output directory if not exists
    path_full_destination = os.path.join(os.getcwd(), output_path)
    if not os.path.exists(path_full_destination):
        os.makedirs(path_full_destination)
        rich_console.console.print(
            "[blue bold][INFO]:[/blue bold] Output directory not found. A new one has been created"
        )

    # Check if output directory has some content already
    elif len(os.listdir(path_full_destination)) > 0:
        rich_console.console.print(
            "[blue bold][INFO]:[/blue bold] The output directory has already some content. Some files may be overwritten"
        )

        auto_clean_output = USER_SETTINGS.get("auto_clean_output")

        confirm_remove = auto_clean_output or Confirm.ask(
            f"\nYou have content in the specified output directory. To start and fill this directory, this script require the output directory to be clean. We can delete all the content in this directory now if you want. Continue?",
            default=False,
        )

        if confirm_remove and auto_clean_output:
            print_warn(
                "You have some files/directories in the specified output directory. Any content here will be removed and replaced by the new data\n"
            )

        if not confirm_remove:
            print_error(
                "The program require the output directory to be clean",
                "Remove all the content in the output directory or specify a new one and re-run the script.",
            )

        for filename in os.listdir(path_full_destination):
            file_path = os.path.join(path_full_destination, filename)

            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print("Failed to delete %s. Reason: %s" % (file_path, e))

    # Wheter the search is recursive in the input folder
    recursive: bool = USER_SETTINGS.get("recursive")  # type: ignore

    filepaths_to_copy = get_filepaths(input_path, recursive)

    console.print(
        f"[blue bold][INFO]:[/blue bold] {len(filepaths_to_copy)} files scanned in the target directory"
    )

    if not USER_SETTINGS.get("include_all_files"):
        filepaths_to_copy = filter_filepaths(
            filepaths_to_copy,
            allowed_ext=set(
                IMG_EXTENSIONS
                + VIDEO_EXTENSIONS
                + (
                    OTHER_ALLOWED_EXTENSIONS
                    if OTHER_ALLOWED_EXTENSIONS is not None
                    else []
                )
            ),
        )

    if len(filepaths_to_copy) == 0:
        console.print(
            "[blue bold][INFO]:[/blue bold] No usefull files for your new organized gallery has been found. Exiting..."
        )
        print()
        quit()

    if not USER_SETTINGS.get("include_all_files"):
        console.print(
            f"[blue bold][INFO]:[/blue bold] {len(filepaths_to_copy)} of that files ({round(100 * len(filepaths_to_copy) / len(get_filepaths(input_path, recursive)),2)}%) have an allowed format, and will be copied to the output directory",
        )
    else:
        console.print(
            f"[blue bold][INFO]:[/blue bold] All the files will be copied to the output directory since the [i]include_all_files[/i] option is true",
        )

    print()

    with progress_bar() as p:
        for path, filename in p.track(
            filepaths_to_copy, description=f"Copying files to [i]./{output_path}[/i]:"
        ):
            file_destination = os.path.join(
                output_path, os.path.relpath(path, input_path)
            )

            if not os.path.exists(file_destination):
                os.makedirs(file_destination)
                rich_console.print_log(
                    f"The subdirectory `{file_destination}` has been created"
                )

            new_filepath = os.path.join(file_destination, filename)

            copy2(
                os.path.join(path, filename),
                new_filepath,
            )

            if not os.path.exists(new_filepath):
                raise Exception("Error copying the file to the output directory")

    if USER_SETTINGS.get("metadata_fixer").get("enabled"):  # type: ignore
        print_separator("Metadata fixer")
        metadata_fixer(
            get_filepaths(output_path, True),
            force_datetime_fix,
            USER_SETTINGS.get("metadata_fixer").get("fill_missing_datetime_info_from"),  # type: ignore
        )

    if USER_SETTINGS.get("file_organizer").get("enabled"):  # type: ignore
        print_separator("Organize files")
        file_organizer(get_filepaths(output_path, True), output_path, folder_structure)

    if USER_SETTINGS.get("duplicates_search").get("enabled"):  # type: ignore
        print_separator("Duplicates search")
        duplicates_remover(
            filter_filepaths(
                get_filepaths(output_path, True),
                allowed_ext=set(IMG_EXTENSIONS),
            ),
            hash_size,
            similarity,
        )

    console.print(
        "[blue bold][INFO]:[/blue bold] Analyzing possible remains of empty directories..."
    )

    folders_removed = remove_empty_folders(os.path.abspath(output_path))

    if len(folders_removed) > 0:
        console.print(
            f"[blue bold][INFO]:[/blue bold] {len(folders_removed)} empty folder(s) has been removed"
        )

    print()
    console.print("[green bold]\u2714 All done! Your gallery is ready!")
 """
