"""
# Shared file tools module
"""
import json
import gzip
import io
import time
import path
import yaml
import sys
import glob, os, shutil
from logging import Logger

# need this before importing from log_tools to prevent relative import issue
sys.path.append(path.Path(__file__).parent.abspath())
from log_tools import log_exceptions


@log_exceptions
def get_yaml_settings(directory, filename):
    with open(f"{directory}/{filename}", "r") as f:
        return yaml.safe_load(f)


@log_exceptions
def get_shared_settings():
    current_directory = path.Path(__file__).parent.abspath()
    return get_yaml_settings(current_directory, "shared_settings.yml")


@log_exceptions
def strip_path_characters(file_or_directory_name: str) -> str:
    """
    Case 1: Single element, e,g, '/logs' returns 'logs'
    Case 2: multiple elements, e,g, './logs/2023/12/1/' returns 'logs/2023/12/1'

    *** do not use anywhere you need an absolute path, this is used for relative paths
    We use this function to make path/directory, or filename clean of characters that imply
     a directory/path.
     We do this to:
       - Allow us to use the OS-indenpendant 'os.path.join()' to create the appropriate
         path statement for the OS the script is running on, e.g., Linux vs Windows ('/' vs '\')
       - Make directory or file names clean to use by removing path characters (/ \ . ..)
       - Make directory or file names clean to use by removing junk characters not supported in paths (~ * # % & { } < > ? = + @ : ; ' " ! $ ` |)
       - Make directory or file names clean to use by removing blank spaces not supported in paths

    This take multiple passes to ensure we strip all bad characters from path items such as './logs$/@' (return 'logs')
    """
    bad_path_chars = [
        " ",
        "~",
        "*",
        ",",
        "#",
        "%",
        "&",
        "{",
        "}",
        "<",
        ">",
        "?",
        "=",
        "+",
        "@",
        ":",
        ";",
        "'",
        '"',
        "!",
        "$",
        "/",
        "\\",
        ".",
        "..",
        "`",
        "|",
    ]
    passes = 10
    i = 0
    file_or_directory_name = str(file_or_directory_name)
    while i <= passes:
        i += 1
        for bad_char in bad_path_chars:
            file_or_directory_name = str(file_or_directory_name).strip(bad_char)
    return file_or_directory_name


@log_exceptions
def separate_path_elements(path_str: str) -> list:
    """
    *** use strip_path_elements() instead if you also want each element cleaned of bad characters
    Takes in a standard path of arbitrary length and returns a list of path elements
    Examples:
        '/dir/dir/dir/file' --> list['dir', 'dir', 'dir', 'file', ]
        './dir/.dir/file/.' --> list['.', 'dir', '.dir', 'file', '.']
        'dir\file' --> list['dir', 'file', ]
    """
    delimiters = ["/", "\\"]
    for delimiter in delimiters:
        path_str = " ".join(path_str.split(delimiter))
    result = path_str.split()
    return result


@log_exceptions
def separate_and_strip_path_elements(path_str: str) -> list:
    """
    Takes in a standard path of arbitrary length and returns a list of path elements
    Examples:
        '../dir/dir/dir/file' --> list['dir', 'dir', 'dir', 'file', ]
        './dir/dir/file/.' --> list['dir', 'dir', 'file']
        'dir\file' --> list['dir', 'file']

    We use strip_path_characters() to clean each path element
    """
    path_elements = separate_path_elements(path_str)
    cleaned_path_elements = []
    for path_element in path_elements:
        cleaned_path_element = strip_path_characters(path_element)
        cleaned_path_elements.append(cleaned_path_element)
    return cleaned_path_elements


@log_exceptions
def format_elapsed_time(elapsed_seconds: float) -> str:
    hours = 0
    minutes = 0
    seconds = 0

    if elapsed_seconds > 3600:
        hours, elapsed_seconds = divmod(elapsed_seconds, 3600)

    if elapsed_seconds > 60:
        minutes, elapsed_seconds = divmod(elapsed_seconds, 60)
    hours = round(hours)
    minutes = round(minutes)
    seconds = round(elapsed_seconds, 2)
    if hours < 10:
        hours = f"0{hours}"
    if minutes < 10:
        minutes = f"0{minutes}"
    if seconds < 10:
        seconds = f"0{seconds}"

    return f"{hours}:{minutes}:{seconds}"


def get_timestamp_for_filename(time_obj: time) -> str:
    # standardized timestamp to append to filename
    return f"{time_obj.strftime('%Y_%m_%d')}"


@log_exceptions
def load_json_file(filename: str) -> dict:
    with open(filename, "r") as openfile:
        json_object = json.load(openfile)
        openfile.close()
        return json_object


@log_exceptions
def to_json_file(json_data: json, filename: str) -> None:
    if not type(json_data) is str:
        json_data = json.dumps(json_data, indent=4)
    with open(filename, "w") as outfile:
        outfile.write(json_data)
        outfile.close()


@log_exceptions
def to_gzip_file(data_text: str, filename: str) -> None:
    with gzip.open(filename, "wb") as output:
        # We cannot directly write Python objects like strings!
        # We must first convert them into a bytes format using io.BytesIO() and then write it
        with io.TextIOWrapper(output, encoding="utf-8") as encode:
            encode.write(data_text)


@log_exceptions
def get_directory_path_from_filepath(filepath):
    path_elements = separate_and_strip_path_elements(filepath)
    dir_path = ""
    for path_element in path_elements[:-1]:
        dir_path = os.path.join(dir_path, path_element)
    return dir_path


@log_exceptions
def gzip_file(filepath, out_dir):
    path_elements = separate_and_strip_path_elements(filepath)
    filename = path_elements[-1]
    file_extension = get_file_extension(filename)

    if file_extension in ["gz", "zip"]:
        # just copy if already zipped
        dst_filepath = os.path.join(out_dir, filename)
        shutil.copyfile(filepath, dst_filepath)
    else:
        # gzip compress file
        compressed_filename = f"{filename}.gz"
        dst_filepath = os.path.join(out_dir, compressed_filename)
        with open(filepath, "rb") as f_in:
            with gzip.open(dst_filepath, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

    return dst_filepath


@log_exceptions
def gzip_files(source_filepaths, out_dir):
    compressed_source_filepaths = []
    for src_filepath in source_filepaths:
        dst_filepath = gzip_file(src_filepath, out_dir)
        compressed_source_filepaths.append(dst_filepath)
    return compressed_source_filepaths


@log_exceptions
def get_file_prefix(filename: str, prefix_delimiter: str, use_logger: Logger = None):
    """
    Get a files prefix based on delimiter (if present),
     or (if not present) return filename without extension

    Args:
        filename (str): file name
        prefix_delimiter (str): str to filename.split('prefix_delimiter')
        use_logger (Logger, optional): _description_. Defaults to None.

    Returns:
        str: file prefix
    """
    if prefix_delimiter in filename:
        # case: we can split on prefix_delimiter, e.g., timestamp '_20'
        prefix = filename.split(prefix_delimiter)[0]
    else:
        # case no prefix_delimiter in filename
        if "." in filename:
            # case: has extension
            prefix = filename.split(".")[0]
        else:
            # case: has no extension
            prefix = filename
        if use_logger:
            use_logger.info(
                f"Cleanup: prefix delimiter '{prefix_delimiter}' not found in '{filename}', using prefix '{prefix}'"
            )
    return prefix


@log_exceptions
def get_file_extension(filename: str):
    """
    Returns a file's extension (if present) or ''

    Args:
        filename (str): file name

    Returns:
        str: .extension or ''
    """
    if "." in filename:
        extension = f".{filename.split('.')[-1]}"
    else:
        extension = ""
    return extension


@log_exceptions
def get_newest_file_of_type_in_folder(folder_path, filename):
    print(f"looking for {filename} in {folder_path}")
    shared_settings = get_shared_settings()
    prefix_delimiter = shared_settings["prefix_delimiter"]
    prefix = get_file_prefix(filename, prefix_delimiter)
    extension = get_file_extension(filename)
    file_list = sorted(
        glob.glob(os.path.join(folder_path, f"{prefix}*{extension}")),
        key=os.path.getmtime,
    )
    file_list.reverse()
    return file_list[0]


@log_exceptions
def get_newest_file_of_each_type_in_folder(folder_path):
    out_file_list = []
    file_types = {}
    shared_settings = get_shared_settings()
    prefix_delimiter = shared_settings["prefix_delimiter"]
    candidate_files = os.listdir(folder_path)
    for candidate_file in candidate_files:
        if candidate_file[0] not in [
            ".",
        ]:
            prefix = get_file_prefix(candidate_file, prefix_delimiter)
            extension = get_file_extension(candidate_file)
            file_type_key = f"{prefix}_{extension}"
            file_type = {
                "prefix": prefix,
                "extension": extension,
            }
            file_types[file_type_key] = file_type
    for file_type_key, file_type in file_types.items():
        filename = f"{file_type['prefix']}{prefix_delimiter}{file_type['extension']}"
        out_file = get_newest_file_of_type_in_folder(folder_path, filename)
        out_file_list.append(out_file)
    return out_file_list


@log_exceptions
def cleanup_files(
    cleanup_dir: str,
    filename: str,
    cleanup_limit: int,
    use_logger: Logger = None,
):
    """
    Cleanup local files based on age

    Args:
        cleanup_dir (str): directory to search for files
        filename (str): file name template to cleanup (see below)
        cleanup_limit (int): number of (newest) files to keep
        use_logger (Logger, optional): logging.Logger to print item deletions, errors, etc.

    Description:
        This uses the filename as a template for gathering other files with the
        same:
        prefix, e.g., 'file_name_2023_12_25.json' -> 'file_name_*'
            and
        extension, e.g., 'file_name_2023_12_25.json' -> 'json'

        It then deletes files with this prefix and extension (oldest first) that
        are above the count 'cleanup_limit'

        For daily jobs, this effectively makes 'cleanup_limit' the number of days to keep
    """

    shared_settings = get_shared_settings()
    prefix_delimiter = shared_settings["prefix_delimiter"]
    prefix = get_file_prefix(filename, prefix_delimiter, use_logger=use_logger)
    extension = get_file_extension(filename)
    # Get the list of all files in the directory with same extension
    #  that start with this prefix (newest first)
    file_list = sorted(
        glob.glob(os.path.join(cleanup_dir, f"{prefix}*{extension}")),
        key=os.path.getmtime,
    )
    file_list.reverse()

    # Delete oldest files if there are more than CLEANUP_LIMIT for cleanup_prefix
    i = 0
    for file in file_list:
        i += 1
        _, extension = os.path.splitext(file)
        if i > cleanup_limit:
            if use_logger:
                use_logger.info(f"cleanup deleting up file {file}")
            os.remove(file)


if __name__ == "__main__":
    print("Example tools (you are running this as a script instead of importing)")
