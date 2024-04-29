from pathlib import Path
from typing import Dict
from uuid import uuid4
from uqload_dl_gui.utils import convert_size
from PyQt5.QtGui import QIcon, QFont, QFontDatabase
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QHBoxLayout,
    QFrame,
)

PARENT_PATH = Path(__file__).parent.parent


class Card(QFrame):
    """
    Widget representing a download card.

    This widget displays information about a download task,
    including the title, download progress, and controls for
    canceling the download.
    """

    download_completed = pyqtSignal()
    cancel_download = pyqtSignal()

    def __init__(self, parent: QWidget, video: Dict[str, str]) -> None:
        """
        Initialize the Card widget.

        Args:
            parent (QWidget): The parent widget.
            video (Dict[str, str]): Information about the video.
        """
        super().__init__()
        self.parent = parent
        self.video = video
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize the user interface of the widget."""

        self.setObjectName("card")
        self.setStyleSheet((PARENT_PATH / "assets/styles/cardDownload.qss").read_text())

        font_path = str(PARENT_PATH / "assets/fonts/nunito-font/Nunito-Regular.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        self.total_size = convert_size(self.video.get("size", 0))  # -> str
        thumbnail = QSvgWidget(str(PARENT_PATH / "assets/icons/video-solid.svg"))
        thumbnail.setFixedSize(26, 26)
        thumbnail.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)

        card_content_frame = QFrame(self)
        card_content_layout = QVBoxLayout(card_content_frame)

        title_frame = QFrame(card_content_frame)
        title_frame_layout = QHBoxLayout(title_frame)
        title_frame_layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel(f"{self.video.get('title',uuid4().hex)}")
        self.title_label.setObjectName("title")
        self.title_label.setFont(QFont(font_family))

        self.format_badge_button = QPushButton(
            f"{self.video.get('type').split('/')[-1]}"
        )
        self.format_badge_button.setFont(QFont(font_family))
        self.format_badge_button.setObjectName("badge_button")
        self.format_badge_button.setEnabled(False)

        self.size_badge_button = QPushButton(f"{self.total_size}")
        self.size_badge_button.setFont(QFont(font_family))
        self.size_badge_button.setEnabled(False)
        self.size_badge_button.setObjectName("badge_button")

        title_frame_layout.addWidget(self.title_label, 2)
        title_frame_layout.addWidget(self.size_badge_button)
        title_frame_layout.addWidget(self.format_badge_button)

        self.bytes_downloaded_label = QLabel(f"0 MB/{self.total_size}")
        self.bytes_downloaded_label.setObjectName("bytes_downloaded_label")
        self.bytes_downloaded_label.setFont(QFont(font_family))

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setTextVisible(False)

        card_content_layout.addWidget(title_frame)
        card_content_layout.addWidget(self.progress_bar)
        card_content_layout.addWidget(self.bytes_downloaded_label)

        self.delete_button = QPushButton(
            icon=QIcon(str(PARENT_PATH / "assets/icons/xmark-solid.svg"))
        )
        self.delete_button.setObjectName("delete_button")
        self.delete_button.clicked.connect(self.cancel_download.emit)

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(thumbnail)
        main_layout.addWidget(card_content_frame, 2)
        main_layout.addWidget(self.delete_button)

    def update_progress(self, value: int) -> None:
        """
        Update the progress bar with the given value.

        Args:
            value (int): The progress value.
        """
        self.progress_bar.setValue(int(value))

    def handle_progress_update(self, bytes_downloaded: int, total: int) -> None:
        """
        Handle progress update.

        This method is called to handle updates to the download progress.
        It updates the progress bar and bytes downloaded label accordingly.

        Args:
            bytes_downloaded (int): The number of bytes downloaded.
            total (int): The total size of the download.
        """
        percentage_complete = int((bytes_downloaded / total) * 100)
        self.progress_bar.setValue(percentage_complete)
        self.bytes_downloaded_label.setText(
            f"{convert_size(bytes_downloaded)} / {self.total_size}"
        )
