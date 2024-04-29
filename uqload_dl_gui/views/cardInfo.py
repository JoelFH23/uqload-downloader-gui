from pathlib import Path
from typing import Dict
from uqload_dl_gui.utils import check_special_characters, convert_size
from PyQt5.QtGui import QIcon, QFontDatabase, QFont
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import (
    QLabel,
    QFrame,
    QWidget,
    QLineEdit,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
)

PARENT_PATH = Path(__file__).parent.parent


class CardInfo(QFrame):
    """
    Widget representing a card for displaying video information and starting downloads.

    This widget provides functionality for displaying video information and starting downloads
    by providing a user interface with input fields and buttons.
    """

    def __init__(self, parent: QWidget) -> None:
        """
        Initialize the CardWidget.

        Args:
            parent (QWidget): The parent widget.
        """
        super().__init__()
        self.parent = parent
        self.is_valid_filename = False
        self.initUI()

    def initUI(self) -> None:
        """Initialize the user interface of the widget."""
        self.setVisible(False)
        self.setObjectName("card_frame")
        self.setStyleSheet((PARENT_PATH / "assets/styles/cardInfo.qss").read_text())

        font_path = str(PARENT_PATH / "assets/fonts/nunito-font/Nunito-Regular.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        card_thumbnail_frame = QFrame(self)
        card_thumbnail_frame.setObjectName("card_thumbnail_frame")
        card_thumbnail_layout = QVBoxLayout(card_thumbnail_frame)
        card_thumbnail_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_thumbnail_layout.setContentsMargins(0, 0, 0, 0)

        thumbnail_image = QSvgWidget(
            str(PARENT_PATH / "assets/icons/file-video-solid.svg")
        )
        thumbnail_image.renderer().setAspectRatioMode(
            Qt.AspectRatioMode.KeepAspectRatio
        )
        card_thumbnail_layout.addWidget(thumbnail_image)

        card_content_frame = QFrame(self)
        card_content_frame.setContentsMargins(0, 0, 0, 0)
        card_content_frame.setObjectName("card_content_frame")
        card_content_layout = QVBoxLayout(card_content_frame)

        self.card_title = QLineEdit()
        self.card_title.setFont(QFont(font_family))
        self.card_title.setObjectName("card_title")
        self.card_title.setPlaceholderText("New Title...")
        self.card_title.textChanged.connect(self.on_change_text)
        self.card_title.returnPressed.connect(self.start_download)

        self.duration_label = QLabel()
        self.video_type_label = QLabel()
        self.video_size_label = QLabel()
        self.duration_label.setFont(QFont(font_family))
        self.video_type_label.setFont(QFont(font_family))
        self.video_size_label.setFont(QFont(font_family))

        card_content_layout.addWidget(self.card_title)
        card_content_layout.addWidget(self.duration_label)
        card_content_layout.addWidget(self.video_type_label)
        card_content_layout.addWidget(self.video_size_label)

        card_button_frame = QFrame(self)
        card_button_frame.setObjectName("card_button_frame")
        card_button_layout = QVBoxLayout(card_button_frame)
        card_button_layout.setContentsMargins(0, 0, 0, 0)
        self.download_button = QPushButton(
            icon=QIcon(str(PARENT_PATH / "assets/icons/file-arrow-down-solid.svg"))
        )
        self.download_button.setObjectName("download_button")
        self.download_button.setIconSize(QSize(18, 18))
        self.download_button.clicked.connect(self.start_download)
        card_button_layout.addWidget(self.download_button)

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(card_thumbnail_frame)
        main_layout.addWidget(card_content_frame)
        main_layout.addWidget(card_button_frame)

    def on_change_text(self) -> None:
        """
        Handle text change event.

        This method is called when the text in the card title input field changes.
        It validates the input text and updates the appearance of the input field accordingly.
        """
        if (
            check_special_characters(self.card_title.text())
            or self.card_title.text().strip() == ""
        ):
            self.card_title.setStyleSheet("color: red; border: none;")
            self.is_valid_filename = False
        else:
            self.card_title.setStyleSheet("color: #cecac3; border: none;")
            self.is_valid_filename = True

    def update_card_info(self, video_info: Dict[str, str]) -> None:
        """
        Update the card with video information.

        This method updates the card with the provided video information,
        including title, duration, video type, and size.

        Args:
            video_info (Dict[str, str]): Information about the video.
        """
        self.card_title.setText(f"{video_info.get('title')}")
        self.duration_label.setText(f"Duration: {video_info.get('duration')}")
        self.video_type_label.setText(f"Type: {video_info.get('type').split('/')[-1]}")
        self.video_size_label.setText(
            f"Size: {convert_size(video_info.get('size', 0))}"
        )

    def start_download(self) -> None:
        """
        Start the download process.

        This method starts the download process when the user clicks the download button.
        It performs validation checks before starting the download.
        """
        if not self.is_valid_filename:
            QMessageBox.critical(
                None, "ERROR", "Invalid Filename!", QMessageBox.StandardButton.Ok
            )
            return
        self.setVisible(False)
        self.parent.send_data()
