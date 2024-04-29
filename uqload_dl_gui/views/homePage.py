from pathlib import Path
from typing import Dict, Any
from uqload_dl_gui.requestThread import RequestThread
from uqload_dl_gui.exceptions import InvalidUQLoadURL
from uqload_dl_gui.utils import validate_uqload_url
from uqload_dl_gui.views.cardInfo import CardInfo
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import (
    QFrame,
    QWidget,
    QLineEdit,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QProgressBar,
    QMessageBox,
)

PARENT_PATH = Path(__file__).parent.parent


class HomePage(QWidget):
    """
    Widget for the home page of the application.

    This widget provides the user interface for the home page,
    including the header with search functionality and a card
    frame for displaying video information.
    """

    data_sent = pyqtSignal(object)

    def __init__(self) -> None:
        """
        Initialize the HomePage widget.

        This method initializes the user interface of the widget
        and initializes the video_info dictionary.
        """
        super().__init__()
        self.init_ui()
        self.video_info = {}

    def init_ui(self) -> None:
        """Initialize the user interface of the widget."""
        self.setStyleSheet((PARENT_PATH / "assets/styles/homePage.qss").read_text())
        font_path = str(PARENT_PATH / "assets/fonts/nunito-font/Nunito-Regular.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        header_frame = QFrame(self)
        header_frame.setObjectName("header_frame")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)

        self.request_progress_bar = QProgressBar()
        self.request_progress_bar.setObjectName("request_progress_bar")
        self.request_progress_bar.setFixedHeight(2)
        self.request_progress_bar.setTextVisible(False)

        search_frame = QFrame(header_frame)
        search_frame.setObjectName("search_frame")

        self.url_input = QLineEdit()
        self.url_input.setFont(QFont(font_family))
        self.url_input.setObjectName("url_input")
        self.url_input.setPlaceholderText("Enter link...")
        self.url_input.returnPressed.connect(self.validate_input)

        self.search_button = QPushButton("Search")
        self.search_button.setFont(QFont(font_family))
        self.search_button.setObjectName("search_button")
        self.search_button.clicked.connect(self.validate_input)

        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(0)
        search_layout.addWidget(self.url_input)
        search_layout.addWidget(self.search_button)

        header_layout.addWidget(self.request_progress_bar)
        header_layout.addWidget(search_frame)

        spacer_item_1 = QSpacerItem(
            60, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        spacer_item_2 = QSpacerItem(
            60, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.card_frame = CardInfo(self)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(header_frame)
        main_layout.addItem(spacer_item_1)
        main_layout.addWidget(self.card_frame)
        main_layout.addItem(spacer_item_2)

    def validate_input(self) -> None:
        """
        Validates the input URL and initiates a request thread.

        This method attempts to validate the URL entered by the user. If the URL
        is valid, it disables UI widgets, starts a request thread using the validated
        URL, and connects success and error signals from the thread to the appropriate
        handler methods (`handle_request_success` and `handle_request_error`).

        Raises:
            InvalidUQLoadURL: If the provided URL is not a valid UQLoad URL.
        """
        try:
            self.disable_widgets()
            self.start_request_thread(validate_uqload_url(self.url_input.text()))
        except InvalidUQLoadURL:
            self.enable_widgets()
            self.show_error_dialog("The provided URL is not a valid UQLoad URL.")
            self.url_input.setFocus()

    def start_request_thread(self, url: str) -> None:
        """
        Starts a request thread with the provided URL.

        This private method creates a `RequestThread` object using the given URL,
        connects its success and error signals to the appropriate handler methods
        (`handle_request_success` and `handle_request_error`), and starts the thread
        execution.

        Args:
            url (str): The validated UQLoad URL to use for the request.
        """
        self.request_thread = RequestThread(url)
        self.request_thread.success_signal.connect(self.handle_request_success)
        self.request_thread.error_signal.connect(self.handle_request_error)
        self.request_thread.start()

    def handle_request_success(self, result: Dict[str, Any]) -> None:
        """
        Handles the successful response of the request.

        This method updates the video information with the result,
        updates the card information, makes the card frame visible,
        enables widgets, and sets focus on the card title.

        Args:
            result (Dict[str, Any]): The result of the successful request.
        """
        self.card_frame.setVisible(True)
        self.video_info = result
        self.card_frame.update_card_info(result)
        self.enable_widgets()
        self.card_frame.card_title.setFocus()

    def handle_request_error(self, error: str) -> None:
        """
        Handles the error response of the request.

        This method hides the card frame, enables widgets, shows
        an error dialog with the given error message, and sets
        focus on the URL input.

        Args:
            error (str): The error message.
        """

        self.enable_widgets()
        self.show_error_dialog(str(error))
        self.url_input.setFocus()

    def disable_widgets(self) -> None:
        """
        Disables UI widgets to indicate ongoing processing.

        This method disables the following UI elements:
            - card_frame: Hides the card frame (likely visual feedback).
            - url_input: Prevents user interaction with the URL input field.
            - search_button: Disables the search button.
            - request_progress_bar: Resets the progress bar range (likely to prepare
              for indeterminate progress).

        This function is typically called before initiating a network request or
        other time-consuming operation to prevent user interaction until the
        process is complete.
        """
        self.card_frame.setVisible(False)
        self.url_input.setDisabled(True)
        self.search_button.setDisabled(True)
        self.request_progress_bar.setRange(0, 0)

    def enable_widgets(self) -> None:
        """
        Enables widgets after request completion.

        This method clears the URL input, enables the URL input
        and search button, and resets the progress bar.
        """
        self.url_input.setText("")
        self.url_input.setDisabled(False)
        self.search_button.setDisabled(False)
        self.request_progress_bar.setRange(0, 100)

    def show_error_dialog(self, message: str) -> None:
        """
        Displays an error dialog.

        This method shows a critical QMessageBox with the given
        error message.

        Args:
            message (str): The error message to display.
        """
        self.message_box = QMessageBox(self)
        self.message_box.setWindowTitle("ERROR")
        self.message_box.setText(message)
        self.message_box.setIcon(QMessageBox.Icon.Critical)
        self.message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.message_box.setDefaultButton(QMessageBox.StandardButton.Ok)
        self.message_box.exec()

    def send_data(self) -> None:
        """
        Sends the collected data.

        This method updates the video information with the card
        title text, emits the data sent signal with the video
        information, and resets the video information to None.
        """
        self.video_info.update(
            {"title": " ".join(self.card_frame.card_title.text().split())}
        )
        self.data_sent.emit(self.video_info)
        self.video_info = None
