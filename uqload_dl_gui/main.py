import sys
from typing import NoReturn
from PyQt5.QtWidgets import QApplication
from uqload_dl_gui.config import get_config
from uqload_dl_gui.views.mainWindow import MainWindow


def main() -> NoReturn:
    get_config()
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
