import pytest
from pytest import MonkeyPatch
from pytestqt.qtbot import QtBot
from uqload_dl_gui.views.cardInfo import CardInfo

video_info = {
    "title": "My first video",
    "video_url": "https://test.com/test.mp4",
    "image_url": "https://test.com/test.png",
    "size": 17000000,
    "type": "video/mp4",
    "duration": "10:59",
}


@pytest.fixture
def app(qtbot: QtBot) -> CardInfo:
    mainWindow = CardInfo(qtbot)
    qtbot.addWidget(mainWindow)
    return mainWindow


def test_card_info(app: CardInfo) -> None:
    app.show()
    assert app.card_title.text() == ""
    assert app.card_title.placeholderText() == "New Title..."


def test_update_card_info(app: CardInfo) -> None:
    app.show()
    assert app.card_title.text() == ""

    app.update_card_info(video_info)

    assert app.card_title.text() == "My first video"
    assert app.duration_label.text() == "Duration: 10:59"
    assert app.video_type_label.text() == "Type: mp4"
    assert app.download_button.isVisible() == True


def test_user_input(app: CardInfo) -> None:
    app.show()
    assert app.card_title.text() == ""
    app.card_title.setText("My video with a new title")
    assert app.card_title.text() == "My video with a new title"
    assert app.is_valid_filename == True


def test_wrong_user_input(app: CardInfo, monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(app, "start_download", lambda _: print("press"))
    app.show()
    app.card_title.setText("Invalid ? user.input")
    assert app.is_valid_filename == False
