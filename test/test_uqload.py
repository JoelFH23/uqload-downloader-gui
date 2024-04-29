import requests_mock, requests, pytest
from typing import List
from pytest import MonkeyPatch
from uqload_dl_gui.uqload import UQLoad
from uqload_dl_gui.utils import remove_special_characters
from uqload_dl_gui.exceptions import InvalidUQLoadURL

html_template = """
<script type='text/javascript'>var player = new Clappr.Player({
        sources: ["https://m180.uqload.to/3rfkv4rhrvw2q4drdkgpxmnva6flydhkehdqtxrb6635d6s4w6jydebrci5q/v.mp4"],
        preload: 'none',
        poster: "https://m180.uqload.to/i/05/02288/vule3vel9n5q_xt.jpg",
        width: "100%",
    height: "100%",
    disableVideoTagContextMenu: true,
        parentId: "#vplayer"
        ,plugins: {"core": [ChromecastPlugin]}
        ,chromecast: { media: {title: "python  $$%%& testing? time!"}, poster: "https://m180.uqload.to/i/05/02288/vule3vel9n5q.jpg" }
        });

</script>
<h1>My video</h1>
<textarea style="min-height:100px;" id="forumcodetext" class="form-control input-lg"
onfocus="copy(this);">[URL=https://uqload.to/vule3vel9n5q.html][IMG]https://m180.uqload.to/i/05/02288/vule3vel9n5q_t.jpg[/IMG]
python  $$%%&amp; testing? time![/URL]
[860x360, 00:22]</textarea>
"""


@pytest.mark.parametrize(
    "url",
    [
        (""),
        ("test"),
        (None),
        (True),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
        (dict),
        (12),
        (3.1416),
        ("xxxxxxxxxxx"),
    ],
)
def test_constructor_incorrect_params(url) -> None:
    with pytest.raises(InvalidUQLoadURL) as exc:
        UQLoad(url)


def test_get_video_info(monkeypatch: MonkeyPatch) -> None:
    uqload = UQLoad("xxxxxxxxxxxx")

    @requests_mock.Mocker()
    def mock_response(m) -> List[requests.Response]:
        m.get(
            "http://uqload.io/xxxxxxxxxxxx.html",
            text=html_template,
        )
        m.get(
            "http://uqload.io/embed-xxxxxxxxxxxx.html",
            text=html_template,
        )
        return [
            requests.get("http://uqload.io/xxxxxxxxxxxx.html"),
            requests.get("http://uqload.io/embed-xxxxxxxxxxxx.html"),
        ]

    @requests_mock.Mocker()
    def mock_head(url, m) -> requests.Response:
        m.head(
            url,
            headers={"content-length": "123", "content-type": "video/mp4"},
            text="ok",
        )
        return requests.head(url)

    monkeypatch.setattr(uqload, "get_responses", mock_response)
    monkeypatch.setattr(uqload, "request_head", lambda url: mock_head(url))

    video_info = uqload.get_info()

    assert video_info.get("size") == 123
    assert video_info.get("type") == "video/mp4"
    assert video_info.get("duration") == "00:22"
    assert video_info.get("resolution") == "860x360"
    assert remove_special_characters(video_info.get("title")) == "My video"
    assert (
        video_info.get("video_url")
        == "https://m180.uqload.to/3rfkv4rhrvw2q4drdkgpxmnva6flydhkehdqtxrb6635d6s4w6jydebrci5q/v.mp4"
    )
