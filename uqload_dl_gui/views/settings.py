import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QDialog,
    QLabel,
    QFileDialog,
    QSpinBox,
    QFrame,
    QFormLayout,
    QGroupBox,
    QMessageBox,
)
from PyQt5.QtGui import QIcon, QKeyEvent, QFontDatabase, QFont
from PyQt5.QtCore import Qt
from uqload_dl_gui.config import get_config

PARENT_PATH = Path(__file__).parent.parent


class Settings(QDialog):
    """
    Dialog for application settings.

    This dialog allows the user to configure various settings such as concurrent downloads,
    maximum queue size, and output folder.
    """

    def __init__(self) -> None:
        """Initialize the Settings dialog."""
        super().__init__()
        self.setFixedSize(600, 124)
        self.setObjectName("settings")
        self.setWindowTitle("Settings")
        self.setWindowIcon(QIcon(str(PARENT_PATH / "assets/icons/gear-solid.svg")))
        self.setStyleSheet((PARENT_PATH / "assets/styles/settings.qss").read_text())
        self.changes_pending = False

        font_path = str(PARENT_PATH / "assets/fonts/nunito-font/Nunito-Regular.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        self.settings = get_config()

        group_box = QGroupBox(self)
        form_layout = QFormLayout(group_box)
        form_layout.setContentsMargins(0, 0, 0, 0)

        self.concurrent_download_spin_box = QSpinBox(group_box)
        self.concurrent_download_spin_box.setFont(QFont(font_family))
        self.concurrent_download_spin_box.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.concurrent_download_spin_box.setRange(2, 5)
        self.concurrent_download_spin_box.setValue(
            int(self.settings.value("concurrent_downloads"))
        )
        self.concurrent_download_spin_box.valueChanged.connect(
            self.on_spin_box_value_changed
        )

        self.max_queue_size_spin_box = QSpinBox(group_box)
        self.max_queue_size_spin_box.setFont(QFont(font_family))
        self.max_queue_size_spin_box.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.max_queue_size_spin_box.setRange(10, 50)
        self.max_queue_size_spin_box.setValue(int(self.settings.value("max_queue")))
        self.max_queue_size_spin_box.valueChanged.connect(
            self.on_spin_box_value_changed
        )

        field = QFrame()
        field_layout = QHBoxLayout(field)
        field_layout.setContentsMargins(0, 0, 0, 0)

        # Label to display selected folder path
        self.folder_label = QLabel(f"{self.settings.value('output_dir')}")
        self.folder_label.setFont(QFont(font_family))
        self.folder_label.setObjectName("folder_label")

        self.change_folder_button = QPushButton(
            icon=QIcon(str(PARENT_PATH / "assets/icons/folder-open-regular.svg")),
            text="Browse...",
        )
        self.change_folder_button.setFont(QFont(font_family))
        self.change_folder_button.clicked.connect(self.select_folder)

        field_layout.addWidget(self.folder_label)
        field_layout.addWidget(self.change_folder_button)

        self.max_size_label = QLabel("Max queue size: ")
        self.max_size_label.setFont(QFont(font_family))

        self.concurrent_downloads_label = QLabel("Concurrent Downloads: ")
        self.concurrent_downloads_label.setFont(QFont(font_family))

        output_folder_label = QLabel("Output Folder: ")
        output_folder_label.setFont(QFont(font_family))

        form_layout.addRow(self.max_size_label, self.max_queue_size_spin_box)
        form_layout.addRow(
            self.concurrent_downloads_label, self.concurrent_download_spin_box
        )
        form_layout.addRow(output_folder_label, field)

        main_layout = QVBoxLayout()
        main_layout.addWidget(group_box)
        self.setLayout(main_layout)

    def on_spin_box_value_changed(self) -> None:
        """
        Handle spin box value changed event.

        This method is called when the value of a spin box is changed.
        It sets the `changes_pending` flag to indicate that changes have been made.
        """
        self.changes_pending = True

    def apply_changes(self) -> None:
        """
        Apply changes made in settings dialog.

        This method applies the changes made in the settings dialog by updating the application settings.
        """
        # update settings
        self.settings.setValue("max_queue", int(self.max_queue_size_spin_box.value()))
        self.settings.setValue(
            "concurrent_downloads", int(self.concurrent_download_spin_box.value())
        )

    def closeEvent(self, event) -> None:
        """
        Override close event.

        This method is called when the dialog is being closed. If there are pending changes,
        it applies the changes and shows a restart message.

        Args:
            event: Close event object.
        """
        if not self.changes_pending:
            return
        self.apply_changes()
        self.show_restart_message()

    def show_restart_message(self) -> None:
        """
        Display restart message.

        This method displays a message box indicating that a restart is required to apply the changes.
        """
        QMessageBox.information(
            self,
            "Restart Required",
            "You need to restart the app to apply the changes.",
            QMessageBox.StandardButton.Ok,
        )
        self.changes_pending = False

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Override key press event.

        This method handles the key press event. If the Escape key is pressed, the dialog is closed.

        Args:
            event (QKeyEvent): Key press event object.
        """
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    def select_folder(self) -> None:
        """
        Select output folder.

        This method opens a file dialog to select the output folder. It updates the folder label
        and sets the `changes_pending` flag if a folder is selected.
        """
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.settings.setValue("output_dir", os.path.normpath(folder_path))
            self.folder_label.setText(f"{os.path.normpath(folder_path)}")
            self.changes_pending = True
