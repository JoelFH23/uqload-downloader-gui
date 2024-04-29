from pathlib import Path
from uqload_dl_gui.views.settings import Settings
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QPropertyAnimation, QRect
from PyQt5.QtWidgets import (
    QFrame,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

PARENT_PATH = Path(__file__).parent.parent


class Sidebar(QFrame):
    """
    Sidebar widget for the main window.

    This class provides a sidebar widget containing buttons for navigating to different sections
    of the application.
    """

    def __init__(self, parent: QWidget) -> None:
        """
        Initialize the Sidebar widget.

        Args:
            parent (QWidget): The parent widget.
        """
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize the user interface of the Sidebar widget."""
        self.setObjectName("sidebar")
        self.setStyleSheet((PARENT_PATH / "assets/styles/sidebar.qss").read_text())

        self.home_button = QPushButton()
        self.home_button.setIcon(QIcon(str(PARENT_PATH / "assets/icons/house.svg")))

        self.downloads_button = QPushButton()
        self.downloads_button.setIcon(
            QIcon(str(PARENT_PATH / "assets/icons/download.svg"))
        )

        spacer_item = QSpacerItem(
            60, 400, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.settings_button = QPushButton()
        self.settings_button.setIcon(
            QIcon(str(PARENT_PATH / "assets/icons/gear-solid.svg"))
        )

        self.sidebar_vertical_layout = QVBoxLayout(self)
        self.sidebar_vertical_layout.setContentsMargins(0, 10, 0, 10)
        self.sidebar_vertical_layout.addWidget(self.home_button)
        self.sidebar_vertical_layout.addWidget(self.downloads_button)
        self.sidebar_vertical_layout.addItem(spacer_item)
        self.sidebar_vertical_layout.addWidget(self.settings_button)

        self.home_button.clicked.connect(lambda: self.parent.change_content(0))
        self.downloads_button.clicked.connect(lambda: self.parent.change_content(1))
        # self.downloads_button.clicked.connect(self.start_animation)
        self.settings = Settings()
        self.settings_button.clicked.connect(lambda: self.settings.exec())

    def start_animation(self) -> None:
        """
        Start the animation for the downloads button.

        This method creates and starts a property animation to make the downloads button shake.
        The animation creates a visual effect to draw the user's attention.
        """
        # Create a property animation for the button's position
        shake_animation = QPropertyAnimation(self.downloads_button, b"geometry", self)

        # Define the shaking range
        shake_range = 5

        # Set up the animation parameters
        shake_animation.setDuration(140)
        shake_animation.setLoopCount(3)  # Number of times to shake
        shake_animation.setEndValue(self.downloads_button.geometry())

        # Shake animation definition
        for i in range(0, shake_animation.loopCount() * 2, 2):
            shake_animation.setKeyValueAt(
                i / (shake_animation.loopCount() * 2),
                QRect(
                    self.downloads_button.x() - shake_range,
                    self.downloads_button.y(),
                    self.downloads_button.width(),
                    self.downloads_button.height(),
                ),
            )
            shake_animation.setKeyValueAt(
                (i + 1) / (shake_animation.loopCount() * 2),
                QRect(
                    self.downloads_button.x() + shake_range,
                    self.downloads_button.y(),
                    self.downloads_button.width(),
                    self.downloads_button.height(),
                ),
            )

        # Start the animation
        shake_animation.start()
