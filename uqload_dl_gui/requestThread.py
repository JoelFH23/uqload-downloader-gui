from PyQt5.QtCore import QThread, pyqtSignal
from uqload_dl_gui.utils import validate_uqload_url
from uqload_dl_gui.uqload import UQLoad


class RequestThread(QThread):
    """
    A custom QThread subclass for handling HTTP requests in a separate thread.

    This class emits signals to indicate the start, success, and error of the request.

    Attributes:
        started_signal (pyqtSignal): Signal emitted when the request thread starts.
        success_signal (pyqtSignal): Signal emitted when the request is successful.
        error_signal (pyqtSignal): Signal emitted when an error occurs during the request.

    Args:
        url (str): The URL for the HTTP request.
    """

    success_signal = pyqtSignal(object)
    error_signal = pyqtSignal(str)

    def __init__(self, url: str) -> None:
        """
        Initialize the RequestThread with the given URL.

        Args:
            url (str): The URL for the HTTP request.
        """
        super().__init__()
        self.url = validate_uqload_url(url)

    def run(self) -> None:
        """
        Execute the HTTP request in a separate thread.

        Emits the success_signal with the video information if the request is successful.
        Emits the error_signal with the error message if an exception occurs during the request.
        """
        try:
            video_info = UQLoad(self.url).get_info()
            self.success_signal.emit(video_info)
        except Exception as ex:
            self.error_signal.emit(str(ex))
