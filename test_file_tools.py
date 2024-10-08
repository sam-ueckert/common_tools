import sys, path
import pytest

sys.path.append(path.Path(__file__).parent.abspath())  # for importing log_tools
from log_tools import log_exceptions, setup_logger
from file_tools import (
    strip_path_characters,
    separate_path_elements,
    separate_and_strip_path_elements,
)


def test_strip_path_characters():
    base_string = "logs"
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

    def create_test_cases():
        test_strings = []
        for bad_path_char in bad_path_chars:
            test_strings.append(f"{bad_path_char}{base_string}{''}")
            test_strings.append(f"{''}{base_string}{bad_path_char}")
            test_strings.append(f"{bad_path_char}{base_string}{bad_path_char}")

            test_strings.append(f"{bad_path_char}{base_string}.{''}")
            test_strings.append(f"{''}{base_string}.{bad_path_char}")
            test_strings.append(f"{bad_path_char}{base_string}.{bad_path_char}")

            test_strings.append(f"{bad_path_char}.{base_string}{''}")
            test_strings.append(f"{''}.{base_string}{bad_path_char}")
            test_strings.append(f"{bad_path_char}.{base_string}{bad_path_char}")

            test_strings.append(f"{bad_path_char}.{base_string}.{''}")
            test_strings.append(f"{''}.{base_string}.{bad_path_char}")
            test_strings.append(f"{bad_path_char}.{base_string}.{bad_path_char}")

            test_strings.append(f".{bad_path_char}.{base_string}.{''}.")
            test_strings.append(f".{''}.{base_string}.{bad_path_char}.")
            test_strings.append(f".{bad_path_char}.{base_string}.{bad_path_char}.")
        return test_strings

    test_cases = create_test_cases()
    for test_case in test_cases:
        print(f"'{test_case}'->'{strip_path_characters(test_case)}'=='{base_string}'")
        assert strip_path_characters(test_case) == base_string


def test_separate_path_elements():
    test_string = "..dir\\.dir/file."
    expected_result = ["..dir", ".dir", "file."]
    result = separate_path_elements(test_string)
    print(f"{test_string}->{result}=={expected_result}")
    assert result == expected_result


def test_separate_and_strip_path_elements():
    test_string = ".dir\\dir./file.."
    expected_result = ["dir", "dir", "file"]
    result = separate_and_strip_path_elements(test_string)
    print(f"{test_string}->{result}=={expected_result}")
    assert result == expected_result


if __name__ == "__main__":
    # pytest -W ignore::UserWarning -v
    test_strip_path_characters()
    test_separate_path_elements()
    test_separate_and_strip_path_elements()
    from file_tools import get_newest_file_of_each_type_in_folder

    newest_files = get_newest_file_of_each_type_in_folder("./")
    print("----------------------------")
    for newest_file in newest_files:
        print(newest_file)
