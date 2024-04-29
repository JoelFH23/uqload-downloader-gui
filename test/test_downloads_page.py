import pytest
from pytest import MonkeyPatch
from pytestqt.qtbot import QtBot
from PyQt5.QtWidgets import QMessageBox
from uqload_dl_gui.views.mainWindow import MainWindow


@pytest.fixture
def app(qtbot: QtBot) -> MainWindow:
    mainWindow = MainWindow()
    qtbot.addWidget(widget=mainWindow)
    return mainWindow


def test_basic_widgets(app: MainWindow) -> None:
    assert app.download_page.cancel_all_button.text() == "Cancel All"
    assert app.download_page.cancel_all_button.isEnabled() == True
    assert app.download_page.total_tasks_label.text() == "0 item(s)"
    assert app.download_page.thread_pool_size == 0


def test_add_to_queue(app: MainWindow, monkeypatch: MonkeyPatch) -> None:
    app.download_page.test_start_download()
    monkeypatch.setattr(
        QMessageBox, "question", lambda *args: QMessageBox.StandardButton.Yes
    )
    assert app.download_page.thread_pool_size == 1
    assert app.download_page.total_tasks_label.text() == "1 item(s)"
    app.download_page.cancel_all()
