import random
from pathlib import Path
from typing import Dict, List
from uqload_dl_gui.customThreadPool import CustomThreadPool
from uqload_dl_gui.views.cardDownload import Card
from uqload_dl_gui.config import get_config
from uqload_dl_gui.worker import Worker
from PyQt5.QtCore import Qt, QMutex, pyqtSignal
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QFrame,
    QLabel,
    QMessageBox,
)

PARENT_PATH = Path(__file__).parent.parent


class DownloadPage(QWidget):
    """
    Widget for managing download tasks.

    This widget provides functionality for managing download tasks, including
    displaying download progress, canceling downloads, and adding new download tasks.
    """

    queue_full_signal = pyqtSignal(str)

    def __init__(self) -> None:
        """
        Initialize the DownloadPage widget.

        This method initializes the user interface of the widget and sets up
        necessary variables and components for managing download tasks.
        """
        super().__init__()
        self.mutex = QMutex()
        self.__mutex2 = QMutex()
        self.errors = 0
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize the user interface of the widget."""
        self.setStyleSheet((PARENT_PATH / "assets/styles/downloadPage.qss").read_text())

        font_path = str(PARENT_PATH / "assets/fonts/nunito-font/Nunito-Regular.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        self.header_frame = QFrame(self)
        self.header_frame.setObjectName("header_frame")
        self.header_frame.setFixedHeight(40)
        self.header_frame_layout = QHBoxLayout(self.header_frame)

        self.total_tasks_label = QLabel("0 item(s)")
        self.total_tasks_label.setFont(QFont(font_family))
        self.total_tasks_label.setObjectName("total_tasks_label")

        self.error_label = QLabel(f"{self.errors} errors")
        self.error_label.setFont(QFont(font_family))
        self.error_label.setObjectName("error_label")

        self.cancel_all_button = QPushButton("Cancel All")
        self.cancel_all_button.setFont(QFont(font_family))
        self.cancel_all_button.setObjectName("cancel_all_button")
        self.cancel_all_button.clicked.connect(self.cancel_all)

        self.create_new_card_button = QPushButton("Add")  # NOTE: only for test!
        self.create_new_card_button.clicked.connect(self.test_start_download)

        self.header_frame_layout.addWidget(self.total_tasks_label, 2)
        self.header_frame_layout.addWidget(self.error_label, 2)
        self.header_frame_layout.addWidget(self.cancel_all_button)
        """ self.header_frame_layout.addWidget(
            self.create_new_card_button
        ) """  # only for test!

        self.card_list = QFrame(self)
        self.card_list.setObjectName("card_list")
        self.card_list_layout = QVBoxLayout(self.card_list)
        self.card_list_layout.setSpacing(10)
        self.card_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("scroll_area")
        self.scroll_area.setWidget(self.card_list)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.header_frame)
        self.main_layout.addWidget(self.scroll_area)

        settings = get_config()
        max_size = int(settings.value("max_queue"))
        max_workers = int(settings.value("concurrent_downloads"))

        self.__thread_pool = CustomThreadPool(max_workers, max_size)
        self.__worker_list: List[Worker] = []

    def start_download(self, video_info: Dict[str, str]) -> None:
        """
        Start a download task.

        This method starts a new download task with the provided video information.
        It creates a new download card and a worker thread for handling the download,
        and submits the worker thread to the thread pool.

        Args:
            video_info (Dict[str, str]): Information about the video to be downloaded.
        """
        if self.__thread_pool.full():
            self.queue_full_signal.emit("The queue is full!")
            return

        card = Card(self, video_info)
        worker = Worker(video_info)
        worker.signals.progress_update.connect(card.handle_progress_update)
        worker.signals.download_completed.connect(
            lambda card_arg=card, runnable=worker: self.on_download_complete(
                card_arg, runnable
            )
        )
        worker.signals.download_error.connect(
            lambda err, card_arg=card, worker_arg=worker: self.on_download_error(
                err, card_arg, worker_arg
            )
        )

        card.cancel_download.connect(
            lambda card_arg=card, runnable=worker: self.cancel_download_dialog(
                card_arg, runnable
            )
        )

        self.__thread_pool.submit_task(worker)
        self.__update_tasks_label()
        self.__worker_list.append(worker)
        self.card_list_layout.addWidget(card)

    def on_download_error(self, error: str, card: Card, worker: Worker) -> None:
        """
        Handle download error.

        This method is called when an error occurs during the download process.
        It removes the worker associated with the error, updates the total tasks,
        and removes the card from the layout.

        Args:
            error (str): The error message.
            card (Card): The card associated with the error.
            worker (Worker): The worker associated with the error.
        """
        try:
            self.mutex.lock()
            print(f"Error downloading the file: {error}")
            self.errors += 1
            self.__worker_list.remove(worker)
            self.__thread_pool.current_tasks = self.__thread_pool.current_tasks - 1
            self.__update_tasks_label()
            self.card_list_layout.removeWidget(card)
            self.error_label.setText(f"{self.errors} errors")
            card.deleteLater()
        except Exception as ex:
            print(str(ex))
        finally:
            self.mutex.unlock()

    def cancel_download_dialog(self, card: Card, worker: Worker) -> None:
        """
        Display cancel download dialog.

        This method displays a dialog asking for confirmation to cancel the download.
        If confirmed, it cancels the download; otherwise, it resumes the download.

        Args:
            card (Card): The card associated with the download.
            worker (Worker): The worker associated with the download.
        """
        worker.pause_download()

        response = self.show_message_dialog(
            "Cancel Download Confirmation",
            "Are you sure you want to cancel the download?",
        )

        if response == QMessageBox.StandardButton.No:
            worker.resume_download()
            return

        self.__cancel_one(card, worker)

    def __cancel_one(self, card: Card, worker: Worker) -> None:
        """
        Cancel a single download.

        This method attempts to cancel a single download. If successful, it deletes
        the associated card and worker.

        Args:
            card (Card): The card associated with the download.
            worker (Worker): The worker associated with the download.
        """
        try:
            if self.__thread_pool.tryTake(worker):
                pass
            else:
                worker.cancel_download()
            self.__delete_card(card, worker)
        except Exception as ex:
            print(str(ex))

    def __remove_all(self) -> None:
        """
        Remove all downloads.

        This method cancels and removes all downloads from the queue.
        """
        try:
            for worker in self.__worker_list:
                if worker.is_running:
                    worker.cancel_download()
                else:
                    self.__thread_pool.tryTake(worker)
            self.__worker_list.clear()

            for i in range(self.card_list_layout.count()):
                self.card_list_layout.itemAt(i).widget().deleteLater()
            self.__update_tasks_label()
        except Exception as ex:
            print(str(ex))

    def __resume_all(self) -> None:
        """
        Resume all downloads.

        This method resumes all paused downloads.
        """
        for worker in self.__worker_list:
            if worker.is_running:
                worker.resume_download()

    def __pause_all(self) -> None:
        """
        Pause all downloads.

        This method pauses all running downloads.
        """
        for worker in self.__worker_list:
            if worker.is_running:
                worker.pause_download()

    def on_download_complete(self, card: Card, worker: Worker) -> None:
        """
        Handle download completion.

        This method is called when a download is completed. It removes
        the associated card and worker.

        Args:
            card (Card): The card associated with the completed download.
            worker (Worker): The worker associated with the completed download.
        """
        try:
            self.mutex.lock()
            self.__delete_card(card, worker)
        except Exception as ex:
            print(str(ex))
        finally:
            self.mutex.unlock()

    def __delete_card(self, card: Card, worker: Worker) -> None:
        """
        Delete a card from the download queue.

        This method removes the specified card and its associated worker
        from the download queue. It also updates the total number of tasks
        in the thread pool and removes the card from the layout.

        Args:
            card (Card): The card to be deleted.
            worker (Worker): The worker associated with the card.
        """
        self.__worker_list.remove(worker)
        self.card_list_layout.removeWidget(card)
        self.__thread_pool.current_tasks = self.__thread_pool.current_tasks - 1
        self.__update_tasks_label()
        card.deleteLater()

    def __update_tasks_label(self) -> None:
        """Update tasks label"""
        self.__mutex2.lock()
        self.total_tasks_label.setText(f"{self.__thread_pool.current_tasks} item(s)")
        self.__mutex2.unlock()

    def cancel_all(self) -> None:
        """
        Cancel all downloads in the queue.

        This method pauses all downloads, prompts the user for confirmation,
        and cancels all downloads if the user confirms. If the user cancels
        the operation, downloads are resumed.
        """
        self.mutex.lock()

        if not self.thread_pool_size:
            self.mutex.unlock()
            return

        self.__pause_all()

        response = self.show_message_dialog(
            "Cancel Download Confirmation",
            "Are you sure you want to cancel all downloads?",
        )

        if response == QMessageBox.StandardButton.Yes:
            self.__remove_all()
        else:
            self.__resume_all()

        self.mutex.unlock()

    def test_start_download(self) -> None:
        """
        Start a test download.

        This method is for testing purposes only. It starts a download
        with randomly generated video information.
        """
        video_info = {
            "title": "Testing",
            "video_url": "https://sample-videos.com/video321/mp4/240/big_buck_bunny_240p_5mb.mp4",
            "image_url": "https://avatars.githubusercontent.com/u/86643583?v=4",
            "size": 5249454,
            "type": "video/mp4",
            "duration": f"{str(random.randint(0, 60)).zfill(2)}:{str(random.randint(0, 60)).zfill(2)}",
        }
        self.start_download(video_info)

    @property
    def thread_pool_size(self) -> int:
        """
        Get the size of the thread pool.

        Returns:
            int: The number of workers in the thread pool.
        """
        return len(self.__worker_list)

    def receive_data(self, video_info: Dict[str, str]) -> None:
        """
        Receive video information and start a download.

        This method receives video information and starts a download
        using the received data.

        Args:
            video_info (Dict[str, str]): A dictionary containing video information.
        """
        self.start_download(video_info)

    def show_message_dialog(
        self, title: str, message: str
    ) -> QMessageBox.StandardButton:
        """
        Show a message dialog.

        This method displays a message dialog with the specified title
        and message.

        Args:
            title (str): The title of the message dialog.
            message (str): The message to be displayed in the dialog.

        Returns:
            QMessageBox.StandardButton: The button clicked by the user.
        """
        return QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
