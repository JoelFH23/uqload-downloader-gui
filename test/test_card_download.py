import pytest
from pytestqt.qtbot import QtBot
from uqload_dl_gui.views.cardDownload import Card
from uqload_dl_gui.utils import convert_size

video_info = {
    "title": "Test Video",
    "video_url": "https://test.com/test.mp4",
    "image_url": "https://test.com/test.png",
    "size": 17000000,
    "type": "video/m4a",
}


@pytest.fixture
def app(qtbot: QtBot) -> Card:
    mainWindow = Card(qtbot, video=video_info)
    qtbot.addWidget(widget=mainWindow)
    return mainWindow


def test_video_info(app: Card) -> None:
    app.show()
    total_size = convert_size(video_info.get("size"))

    assert app.isVisible()
    assert app.progress_bar.isVisible()
    assert app.size_badge_button.isVisible()
    assert app.title_label.text() == "Test Video"
    assert app.bytes_downloaded_label.text() == f"0 MB/{total_size}"
    assert app.size_badge_button.text() == total_size


def test_progress_bar_update(app: Card) -> None:
    app.show()
    assert app.progress_bar.isVisible()
    assert app.progress_bar.text() == ""
    app.progress_bar.setValue(20)
    assert app.progress_bar.text() == "20%"

    app.handle_progress_update(50000000, video_info.get("size"))
    assert app.bytes_downloaded_label.text() == "47.68 MB / 16.21 MB"
    assert app.format_badge_button.text() == "m4a"
