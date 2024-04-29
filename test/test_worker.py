import pytest, time, os, requests_mock
from pytest import MonkeyPatch
from pytestqt.qtbot import QtBot
from uqload_dl_gui.worker import Worker

video_info = {
    "title": "my video",
    "video_url": "https://sample-videos.com/video321/mp4/240/big_buck_bunny_240p_5mb.mp4",
}


@pytest.mark.parametrize(
    "video_info", [(""), (True), ([]), ("test"), ({}), (123), (-12.3)]
)
def test_incorrect_params(video_info) -> None:
    with pytest.raises(ValueError):
        Worker(video_info)


def test_download(qtbot: QtBot, monkeypatch: MonkeyPatch) -> None:
    worker = Worker(video_info)

    def mock_download() -> None:
        worker.signals.download_started.emit()
        print("downloading...")
        time.sleep(0.3)
        worker.signals.download_completed.emit()

    monkeypatch.setattr(worker, "_Worker__download", mock_download)

    with qtbot.waitSignal(worker.signals.download_completed):
        worker.run()


def test_download_cancel_by_the_user(qtbot: QtBot) -> None:
    worker = Worker(video_info)

    with qtbot.waitSignal(
        signal=worker.signals.download_cancelled, timeout=3000
    ) as blocker:
        blocker.connect(worker.signals.download_error)
        worker.cancel_download()
        worker.run()

    try:
        os.remove(worker.destination_path)
    except Exception as ex:
        print(str(ex))


def test_missing_content_length(qtbot: QtBot) -> None:
    with requests_mock.Mocker() as mock:
        mock.get("http://my_video.com/video.mp4", text="response")

        worker = Worker({"video_url": "http://my_video.com/video.mp4"})
        with qtbot.waitSignal(worker.signals.download_error, timeout=2000) as blocker:
            worker.run()
        assert blocker.args[0] == "Content-Length header is missing"


def test_non_200_status_code_error(qtbot: QtBot) -> None:
    with requests_mock.Mocker() as mock:
        mock.get("http://my_video.com/video.mp4", text="response", status_code=401)

        worker = Worker({"video_url": "http://my_video.com/video.mp4"})
        with qtbot.waitSignal(worker.signals.download_error, timeout=2000) as blocker:
            worker.run()
        assert blocker.args[0] == "Unexpected status code: 401"
