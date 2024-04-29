import pytest
from pytest import MonkeyPatch
from uqload_dl_gui.concurrentRequester import ConcurrentRequester


@pytest.mark.parametrize(
    "urls",
    [
        (""),
        (True),
        (False),
        (object),
        (34.3),
        ([]),
        ({}),
        ({"title": "video"}),
    ],
)
def test_incorrect_user_input(urls) -> None:
    with pytest.raises(ValueError) as excinfo:
        ConcurrentRequester(urls).run_concurrent_requests()
    assert "urls must be a non-empty list" in str(excinfo.value)


def test_get_responses_with_status_code_ok(monkeypatch: MonkeyPatch) -> None:
    urls = ["https://test.com/"] * 10
    concurrent_requester = ConcurrentRequester(urls)

    def mock_get(*args) -> None:
        concurrent_requester.responses.append((args[2], 200))

    monkeypatch.setattr(ConcurrentRequester, "fetch_url", mock_get)
    result = concurrent_requester.run_concurrent_requests()
    assert len(result) == 10
    assert 200 in result


def test_get_responses_with_non_200_status_code(monkeypatch: MonkeyPatch) -> None:
    urls = ["https://test.com/"] * 10
    concurrent_requester = ConcurrentRequester(urls)

    def mock_get(*args) -> None:
        concurrent_requester.responses.append((args[2], None))

    monkeypatch.setattr(ConcurrentRequester, "fetch_url", mock_get)
    result = concurrent_requester.run_concurrent_requests()
    assert len(result) == 10
    assert None in result
