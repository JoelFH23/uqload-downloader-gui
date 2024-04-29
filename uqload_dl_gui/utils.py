import re, math
from uqload_dl_gui.exceptions import InvalidUQLoadURL


def check_special_characters(input_string) -> bool:
    """
    Check if a string contains any of the special characters.

    Args:
        input_string (str): The input string to check.

    Returns:
        bool: True if the input string contains any of the special characters, False otherwise.

    Raises:
        ValueError:

    """
    if not isinstance(input_string, str) or not len(input_string):
        raise ValueError("Invalid input string")

    special_characters = set(["<", ">", ":", '"', "/", "\\", "|", "?", "*", "."])

    for char in input_string:
        if char in special_characters:
            return True

    return False


def is_uqload_url(url: str) -> bool:
    """
    Checks if the provided URL is a valid Uqload URL.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if the URL is a valid Uqload URL, False otherwise.
    """
    if url is None:
        return False
    uqload_regex = (
        r"^https?://(www\.)?uqload\.[a-z]+/(embed\-)?[a-zA-Z0-9]{12}\.(html)$"
    )
    if not isinstance(url, str) or not re.match(uqload_regex, url):
        return False
    return True


def validate_uqload_url(url: str) -> str:
    """
    Validate the Uqload URL.

    Args:
        url (str): A string representing the input Uqload URL.

    Returns:
        str: A validated and formatted Uqload URL.

    Raises:
        InvalidUQLoadURL: If the input URL is None, not a string, shorter than 12 characters,
        or doesn't follow the expected Uqload URL format.
    """
    # Check if the input URL is a string and has a minimum length of 12 characters
    if url is None or not isinstance(url, str) or len(url) < 12:
        raise InvalidUQLoadURL("Invalid Uqload URL. Please try again.")

    # Split the URL into two parts: base URL and video ID
    list_of_url = url.rsplit("/", 1)

    # Extract base URL from the split parts, or use a default if no base URL is present
    base_url = list_of_url[0] if len(list_of_url) == 2 else "https://uqload.to"
    video_id = list_of_url[-1]

    # Add ".html" to the video ID if it's not already present
    video_id = f"{video_id}.html" if ".html" not in video_id else video_id
    # Add "embed-" to the video ID if it's not already present
    video_id = f"embed-{video_id}" if "embed-" not in video_id else video_id

    full_url = f"{base_url}/{video_id}"

    # Check if the full URL is a valid Uqload URL
    if not is_uqload_url(full_url):
        raise InvalidUQLoadURL("Invalid Uqload URL. Please try again.")

    return full_url


def remove_special_characters(input_string: str) -> str:
    """
    Removes special characters from a string.

    Note: if only invalid characters are entered, an empty string will be returned.

    Args:
        input_string (str): The input string to clean.

    Returns:
        str: The cleaned string.
    """
    if (
        input_string is None
        or not isinstance(input_string, str)
        or not len(input_string)
    ):
        raise ValueError("input_string must be a non-empty string")
    cleaned_string = re.sub('[<>:"/\\|?*.]', " ", input_string)

    return " ".join((cleaned_string.split()))


def convert_size(size_bytes: int) -> str:
    """Converts a file size in bytes to a human-readable string.

    Args:
        size_bytes (int): The size of the file in bytes.

    Returns:
        str: A human-readable string representing the file size, including units
        (e.g., "10.5 KB").
    """
    if type(size_bytes) is not int or size_bytes <= 0:
        return "0B"
    size_units = ("B", "KB", "MB", "GB")
    size_index = int(math.floor(math.log(size_bytes, 1024)))

    base = 1024**size_index
    human_readable_size = round(size_bytes / base, 2)
    return f"{human_readable_size} {size_units[size_index]}"
