import pytest
from pytestqt.qtbot import QtBot
from uqload_dl_gui.views.mainWindow import MainWindow


@pytest.fixture
def app(qtbot: QtBot) -> MainWindow:
    mainWindow = MainWindow()
    qtbot.addWidget(widget=mainWindow)
    return mainWindow


def test_basics(app: MainWindow) -> None:
    app.show()
    assert app.isVisible()
    assert app.windowTitle() == "Uqload Downloader GUI"
    assert app.stacked_widget.currentIndex() == 0
    assert app.stacked_widget.isVisible() == True


def test_sidebar(app: MainWindow) -> None:
    assert app.stacked_widget.currentIndex() == 0
    app.stacked_widget.setCurrentIndex(1)
    assert app.stacked_widget.currentIndex() == 1

    app.sidebar.home_button.click()
    assert app.stacked_widget.currentIndex() == 0

    app.sidebar.downloads_button.click()
    assert app.stacked_widget.currentIndex() == 1
