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
import glob, os

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
def cleanup_files(cleanup_dir, cleanup_prefix, cleanup_limit, use_logger=None):
    """
    Cleanup local files
    """
    shared_settings = get_shared_settings()
    prefix_delimiter = shared_settings["prefix_delimiter"]
    # Get the list of all files in the directory that start with output_file
    if prefix_delimiter in cleanup_prefix:
        cleanup_prefix = cleanup_prefix.split(prefix_delimiter)[0]
    file_list = glob.glob(os.path.join(cleanup_dir, cleanup_prefix + "*"))
    # Create a dict to count the number of files for each extension
    extension_counts = {}

    for file in file_list:
        _, extension = os.path.splitext(file)
        if extension not in extension_counts:
            extension_counts[extension] = 1
        else:
            extension_counts[extension] += 1

    # Delete files if there are more than CLEANUP_LIMIT for cleanup_prefix
    for file in file_list:
        _, extension = os.path.splitext(file)
        if extension_counts[extension] > cleanup_limit:
            if use_logger:
                use_logger.info(f"cleaning up file {file}")
            os.remove(file)
            extension_counts[extension] -= 1


if __name__ == "__main__":
    print("Example tools (you are running this as a script instead of importing)")
