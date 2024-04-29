import pytest
from pytest import MonkeyPatch
from pytestqt.qtbot import QtBot
from uqload_dl_gui.requestThread import RequestThread
from uqload_dl_gui.exceptions import InvalidUQLoadURL


@pytest.mark.parametrize(
    "value", [(""), ("123"), (True), (False), (object), ([]), (["assd"]), ({})]
)
def test_incorrect_params(value) -> None:
    with pytest.raises(InvalidUQLoadURL) as e_info:
        RequestThread(value)
    assert "Invalid Uqload URL. Please try again." in str(e_info.value)


def test_with_request_ok(qtbot: QtBot, monkeypatch: MonkeyPatch) -> None:
    request_thread = RequestThread("https://uqload.com/embed-xxxxxxxxxxxx.html")

    def mock_get_video() -> None:
        request_thread.success_signal.emit("Testing is fun in Python")

    monkeypatch.setattr(request_thread, "run", mock_get_video)

    with qtbot.waitSignal(request_thread.finished, timeout=7500) as blocker:
        blocker.connect(request_thread.success_signal)
        blocker.connect(request_thread.error_signal)
        request_thread.start()

    assert blocker.args == ["Testing is fun in Python"]


def test_with_request_failed(qtbot: QtBot, monkeypatch: MonkeyPatch) -> None:
    request_thread = RequestThread("thebestvideo")

    def mock_get_video() -> None:
        request_thread.error_signal.emit("Video not found!")

    monkeypatch.setattr(request_thread, "run", mock_get_video)

    with qtbot.waitSignal(request_thread.finished, timeout=7500) as blocker:
        blocker.connect(request_thread.success_signal)
        blocker.connect(request_thread.error_signal)
        request_thread.start()

    assert blocker.args == ["Video not found!"]
