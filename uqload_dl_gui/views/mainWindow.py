from typing import Dict
from pathlib import Path
from uqload_dl_gui.views.downloadPage import DownloadPage
from uqload_dl_gui.views.homePage import HomePage
from uqload_dl_gui.views.sidebar import Sidebar
from PyQt5.QtGui import QKeyEvent, QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QMainWindow,
    QHBoxLayout,
    QStackedWidget,
    QMessageBox,
)

PARENT_PATH = Path(__file__).parent.parent


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize the user interface of the main window."""
        self.setMinimumSize(800, 600)
        self.setWindowTitle("Uqload Downloader GUI")
        self.setWindowIcon(QIcon(str(PARENT_PATH / "assets/icons/camera_video.ico")))
        self.setStyleSheet((PARENT_PATH / "assets/styles/mainWindow.qss").read_text())

        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("mainWindow")

        # Sidebar
        self.sidebar = Sidebar(self)
        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.setObjectName("content")

        # Pages
        self.home_page = HomePage()
        self.download_page = DownloadPage()
        self.home_page.data_sent.connect(self.on_submit)
        self.download_page.queue_full_signal.connect(self.home_page.show_error_dialog)

        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.download_page)

        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.stacked_widget)
        self.setCentralWidget(self.central_widget)

    def on_submit(self, video_info: Dict[str, str]) -> None:
        """
        Triggers an animation on the sidebar and sends data to the download page for processing.

        Args:
            video_info (dic): The data submitted by the user.
        """
        self.sidebar.start_animation()
        self.download_page.receive_data(video_info)

    def change_content(self, index: int) -> None:
        """
        Changes the content displayed by the stacked widget to the specified index.

        Args:
            index: The index of the widget to be displayed within the stacked widget.
        """
        self.stacked_widget.setCurrentIndex(index)

    def show_message_dialog(self) -> QMessageBox.StandardButton:
        """
        Displays a message dialog asking the user if they want to close the window.

        Returns:
            QMessageBox.StandardButton: The button clicked by the user (Yes or No).
        """
        return QMessageBox.question(
            self,
            "Exit",
            "Are you sure you want to close the window?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

    def closeEvent(self, event: QKeyEvent) -> None:
        """
        Overrides the close event for the window.

        If there are no active downloads, the event is accepted and the window closes.
        If there are active downloads, they are paused,
        and a message dialog prompts the user to confirm closing the window.
        If the user confirms, all downloads are removed, and the event is accepted, closing the window.
        If the user cancels, all downloads are resumed, and the event is ignored.

        Args:
            event (QKeyEvent): The close event.
        """
        if not self.download_page.thread_pool_size:
            event.accept()
            return

        self.download_page.pause_all()

        if self.show_message_dialog() == QMessageBox.StandardButton.Yes:
            self.download_page.remove_all()
            event.accept()
            return
        self.download_page.resume_all()
        event.ignore()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Overrides the key press event for the window.

        If the Escape key is pressed and there are no active downloads, the window is closed.
        If the Escape key is pressed and there are active downloads,
        they are paused, and a message dialog prompts the user to confirm closing the window.
        If the user confirms, all downloads are removed, and the window is closed.
        If the user cancels, all downloads are resumed.

        Args:
            event (QKeyEvent): The key press event.
        """
        if event.key() == Qt.Key.Key_Escape:
            if not self.download_page.thread_pool_size:
                self.close()
                return

            self.download_page.pause_all()

            if self.show_message_dialog() == QMessageBox.StandardButton.Yes:
                self.download_page.remove_all()
                self.close()
                return
            self.download_page.resume_all()
