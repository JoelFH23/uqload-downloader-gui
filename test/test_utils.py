import pytest
from uqload_dl_gui.utils import (
    check_special_characters,
    remove_special_characters,
    convert_size,
    is_uqload_url,
    validate_uqload_url,
)


@pytest.mark.parametrize("input_string", [(""), (True), (123), (13.2), ([]), ({})])
def test_invalid_input_string(input_string) -> None:
    with pytest.raises(ValueError):
        check_special_characters(input_string)


@pytest.mark.parametrize(
    "url",
    [
        (""),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
        (True),
        (False),
        (None),
        (1050),
        (0),
        (15.25),
        ("abcdefghijkl"),
        ([]),
    ],
)
def test_invalid_uqload_url(url) -> None:
    assert is_uqload_url(url) == False


def test_invalid_uqload_url_2() -> None:
    assert is_uqload_url("https://uqload.io/embed-abcdefghijkl.html") == True
    assert is_uqload_url("https://uqload.io/abcdefghijkl.html") == True


def test_validate_uqload_url() -> None:
    assert (
        validate_uqload_url("abcdefghijkl")
        == "https://uqload.io/embed-abcdefghijkl.html"
    )


@pytest.mark.parametrize(
    "input_string",
    [("test/"), ("test?"), ("test*test"), ("test1|test2"), ('test"ing')],
)
def test_string_with_special_characters(input_string) -> None:
    assert check_special_characters(input_string) == True


def test_remove_special_characters() -> None:
    assert remove_special_characters("testing...") == "testing"
    assert remove_special_characters("5 > 3") == "5 3"
    assert remove_special_characters("age: 20") == "age 20"
    assert remove_special_characters("Python") == "Python"
    assert remove_special_characters("Python3.9") == "Python3 9"


@pytest.mark.parametrize("size_bytes", [(""), (True), (123.1), (-12), ("test"), ([])])
def test_invalid_size(size_bytes) -> None:
    assert convert_size(size_bytes) == "0B"


def test_convert_size() -> None:
    assert convert_size(100000000) == "95.37 MB"
    assert convert_size(659874523) == "629.31 MB"
    assert convert_size(2015477) == "1.92 MB"
