import pytest
from PyQt5.QtCore import QTimer
from pytestqt.qtbot import QtBot
from PyQt5.QtWidgets import QMessageBox
from uqload_dl_gui.views.mainWindow import MainWindow


@pytest.fixture
def app(qtbot: QtBot) -> MainWindow:
    mainWindow = MainWindow()
    qtbot.addWidget(widget=mainWindow)
    return mainWindow


def test_home_page(app: MainWindow) -> None:

    assert app.home_page.request_progress_bar.isVisible() == False
    assert app.home_page.card_frame.isVisible() == False
    assert app.home_page.url_input.text() == ""

    app.home_page.url_input.setText("Testing is fun in Python")
    assert app.home_page.url_input.text() != ""
    assert app.home_page.url_input.text() == "Testing is fun in Python"

    app.home_page.url_input.clear()
    assert app.home_page.url_input.text() == ""

    assert app.home_page.search_button.text() == "Search"

    assert app.home_page.video_info == {}


def test_show_error_message_box(app: MainWindow) -> None:
    app.home_page.url_input.setText("xxxxxxxxxxx")

    timer = QTimer()
    timer.singleShot(500, lambda: app.home_page.message_box.defaultButton().click())

    app.home_page.search_button.click()

    assert (
        app.home_page.message_box.text()
        == "The provided URL is not a valid UQLoad URL."
    )
    assert app.home_page.message_box.windowTitle() == "ERROR"
    assert app.home_page.message_box.icon() == QMessageBox.Icon.Critical
    assert app.home_page.card_frame.isVisible() == False


def test_show_card_info(app: MainWindow, qtbot: QtBot) -> None:
    app.home_page.url_input.setText("https://uqload.to/vule3vel9n5q.html")
    app.home_page.search_button.click()

    with qtbot.waitSignal(
        signal=app.home_page.request_thread.finished, timeout=14000
    ) as blocker:
        blocker.connect(app.home_page.request_thread.success_signal)
        blocker.connect(app.home_page.request_thread.error_signal)

    assert len(blocker.args) == 1
    assert (
        blocker.args[0].get("image_url")
        == "https://m180.uqload.to/i/05/02288/vule3vel9n5q_xt.jpg"
    )
    assert blocker.args[0].get("title") == "python $$%%& testing time!"
