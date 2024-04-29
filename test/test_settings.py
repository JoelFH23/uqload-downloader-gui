import pytest
from pytestqt.qtbot import QtBot
from uqload_dl_gui.views.settings import Settings


@pytest.fixture
def app(qtbot: QtBot) -> Settings:
    mainWindow = Settings()
    qtbot.addWidget(widget=mainWindow)
    return mainWindow


def test_basic(app: Settings) -> None:
    app.show()
    assert app.isVisible() == True
    assert app.windowTitle() == "Settings"

    assert app.max_size_label.text() == "Max queue size: "
    assert app.concurrent_downloads_label.text() == "Concurrent Downloads: "
    assert app.change_folder_button.text() == "Browse..."
