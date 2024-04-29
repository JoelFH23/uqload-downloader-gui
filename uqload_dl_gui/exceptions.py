class Non200StatusCodeError(Exception):
    """A non-200 status code is encountered in a response."""

    pass


class MissingContentLengthError(Exception):
    """Ccontent length is missing in a response."""

    pass


class InvalidUQLoadURL(Exception):
    """Invalid UQLoad URL is detected."""

    pass


class DownloadCancelledError(Exception):
    """Download operation is cancelled."""

    pass


class VideoNotFoundError(Exception):
    """Requested video is not found."""

    pass
