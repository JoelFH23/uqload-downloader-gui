import time, random, requests, os
from typing import Dict
from uuid import uuid4
from threading import Event
from urllib.parse import urlparse
from PyQt5.QtCore import pyqtSignal, QObject, QRunnable
from uqload_dl_gui.config import get_config
from uqload_dl_gui.exceptions import (
    MissingContentLengthError,
    Non200StatusCodeError,
    DownloadCancelledError,
)


class Signals(QObject):
    """
    Custom signals emitted by the Worker class during different stages of the download process.

    Signals:
        progress_update: Emitted to update the progress of the download.
        download_started: Emitted when the download process starts.
        download_completed: Emitted when the download process is successfully completed.
        download_cancelled: Emitted when the download process is cancelled by the user.
        download_error: Emitted when an error occurs during the download process.
    """

    progress_update = pyqtSignal(int, int)
    download_started = pyqtSignal()
    download_completed = pyqtSignal()
    download_cancelled = pyqtSignal()
    download_error = pyqtSignal(str)


class Worker(QRunnable):
    """
    A worker class for downloading videos.

    This class represents a worker responsible for downloading videos from a given URL.

    Attributes:
        video_info (Dict[str, str]): A dictionary containing information about the video,
        including title and video URL.
    """

    def __init__(self, video_info: Dict[str, str]) -> None:
        """
        Initialize the Worker instance with video information.

        Args:
            video_info (Dict[str, str]): A dictionary containing information about the video,
            including title and video URL.
        """
        super().__init__()
        self.video_info = self.__validate_video_info(video_info)
        self.__pause_event = Event()
        self.signals = Signals()
        self.__cancelled = False
        self.is_running = False
        self.__output_dir = self.__validate_output_dir(get_config().value("output_dir"))
        self.__pause_event.set()

    def __validate_video_info(self, video_info: Dict[str, str]) -> None:
        if not isinstance(video_info, dict) or not len(video_info):
            raise ValueError("video_info must be a dict")
        return video_info

    def __validate_output_dir(self, output_dir: str) -> str:
        """
        Validate the output directory and return the normalized directory path.

        If the provided output directory does not exist, the current working directory is used.

        Args:
            output_dir (str): The output directory path to be validated.

        Returns:
            str: The validated and normalized output directory path.
        """
        if not os.path.isdir(output_dir):
            current_directory = os.getcwd()
            get_config().setValue("output_dir", os.path.normpath(current_directory))
            return current_directory
        return output_dir

    def run(self) -> None:
        """Run the worker task, initiating the download process."""
        self.__download()

    def __download(self) -> None:
        """Initiate the download process of the video."""
        try:
            url = self.video_info.get("video_url", None)
            filename = self.video_info.get("title", None)

            if not isinstance(url, str) or not len(url):
                raise ValueError("URL must be a non empty string")

            parsed_url = urlparse(url)
            self.headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36",
                "Referer": f"{parsed_url.scheme}://{parsed_url.netloc}",
            }

            # Get filename and extension from the URL
            root, ext = os.path.splitext(os.path.basename(parsed_url.path))
            if root == "" or ext == "":
                raise ValueError("URL must be a non empty string")

            filename = root if filename is None or filename == "" else filename

            self.destination_path = os.path.join(self.__output_dir, f"{filename}{ext}")

            # check if the file already exist
            if os.path.isfile(self.destination_path):
                self.destination_path = os.path.join(
                    self.__output_dir,
                    f"{filename}_{uuid4().hex}{ext}",
                )

            # self.__download_test(url)
            self.__download_file(url)
        except Exception as ex:
            print(str(ex))
            self.on_download_error(str(ex))

    def start_download(self) -> None:
        """Start the download process."""
        self.is_running = True
        self.signals.download_started.emit()

    def cancel_download(self) -> None:
        """Cancel the download process."""
        self.__cancelled = True
        self.__pause_event.set()

    def on_download_cancelled(self) -> None:
        """Handle the case when the download is cancelled."""
        print("Download cancelled. Incomplete file may be saved.")
        self.signals.download_cancelled.emit()

    def on_download_complete(self) -> None:
        """Handle the case when the download is completed successfully."""
        print(f"Download successful. File saved to: {self.__output_dir}")
        self.signals.download_completed.emit()

    def on_download_error(self, error: str) -> None:
        """
        Handle the case when an error occurs during the download.

        Args:
            error (str): The error message.
        """
        self.signals.download_error.emit(str(error))

    def pause_download(self) -> None:
        """Pause the download process."""
        self.__pause_event.clear()

    def resume_download(self) -> None:
        """Resume the download process."""
        self.__pause_event.set()

    def is_paused(self) -> None:
        """Check if the download is currently paused."""
        self.__pause_event.wait()

    def is_download_cancelled(self) -> None:
        """
        Check if the download has been cancelled.

        Raises:
            DownloadCancelledError: If the download has been cancelled.
        """
        if self.__cancelled:
            raise DownloadCancelledError("Download cancelled by the user.")

    def __progress(self, bytes_downloaded: int, total: int) -> None:
        """
        Emit a signal to update the progress of the download.

        This method emits a signal to update the progress of the download, indicating the
        number of bytes downloaded and the total size of the file.

        Args:
            bytes_downloaded (int): The number of bytes downloaded so far.
            total (int): The total size of the file being downloaded.
        """
        self.signals.progress_update.emit(bytes_downloaded, total)

    def __download_test(self, url: str) -> None:
        """
        Download test method for simulation purposes.

        Args:
            url (str): The URL of the file to be simulated for download.

        Raises:
            DownloadCancelledError: If the download is cancelled by the user.
        """
        try:
            self.start_download()
            total_size = int(self.video_info.get("size", 0))
            bytes_downloaded = 0

            error = True if random.randint(0, 1) else False

            while bytes_downloaded < total_size:
                self.is_paused()
                self.is_download_cancelled()
                chunk = random.randint(10000, 100000)

                if error:
                    time.sleep(random.random() * 2)
                    raise ValueError("Request Error")

                bytes_downloaded += chunk
                if bytes_downloaded >= total_size:
                    bytes_downloaded = total_size
                self.__progress(bytes_downloaded, total_size)

                time.sleep(0.04)
                # time.sleep(random.random())
            self.on_download_complete()

        except DownloadCancelledError:
            self.on_download_cancelled()
        except Exception as ex:
            print(str(ex))
            self.on_download_error(str(ex))
        finally:
            self.is_running = False

    def __download_file(self, url: str) -> None:
        """
        Download a file from the given URL.

        Args:
            url (str): The URL of the file to be downloaded.

        Raises:
            ValueError: If the URL is an empty string.
            requests.exceptions.RequestException: If there is an issue with the HTTP request.
            Non200StatusCodeError: If there is a non-200 status code.
            MissingContentLengthError: If the 'Content-Length' header is missing.
        """
        try:
            with requests.get(
                url, stream=True, headers=self.headers, timeout=20
            ) as response:

                if response.status_code != 200:
                    raise Non200StatusCodeError(
                        f"Unexpected status code: {response.status_code}"
                    )

                total_size = int(response.headers.get("content-length", 0))

                if not total_size:
                    raise MissingContentLengthError("Content-Length header is missing")

                self.start_download()
                bytes_downloaded = 0
                with open(self.destination_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=10 * 1024):
                        self.is_paused()
                        self.is_download_cancelled()
                        bytes_downloaded += len(chunk)
                        self.__progress(bytes_downloaded, total_size)
                        file.write(chunk)
                self.on_download_complete()
        except Non200StatusCodeError as e:
            self.on_download_error(str(e))
        except MissingContentLengthError as e:
            self.on_download_error(str(e))
        except DownloadCancelledError:
            self.on_download_cancelled()
        finally:
            self.is_running = False
