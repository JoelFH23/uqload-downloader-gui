import re
from typing import Dict, List, Union
from urllib.parse import urlparse
from requests import Response
from uqload_dl_gui.concurrentRequester import ConcurrentRequester
from uqload_dl_gui.exceptions import VideoNotFoundError
from uqload_dl_gui.utils import validate_uqload_url, remove_special_characters


class UQLoad:
    """
    A class for extracting video information from UQLoad URLs.

    This class retrieves video information including title, video URL, image URL, size, type, resolution, and duration
    from a UQLoad URL.

    Attributes:
        url (str): The UQLoad URL from which to extract video information.

    Raises:
        InvalidUQLoadURL: If the provided URL is not a valid UQLoad URL.
    """

    def __init__(self, url: str) -> None:
        """
        Initialize the UQLoad instance with the provided URL.

        Args:
            url (str): The UQLoad URL from which to extract video information.
        """
        self.__video_info = {}
        self.url = validate_uqload_url(url)

    def get_responses(self) -> List[Union[Response, None]]:
        """
        Fetches responses from the URLs and returns them.

        Returns:
            List[Union[Response, None]]: List of responses or None.

        Raises:
            Exception: If None is found in responses.
        """
        urls = [self.url, self.url.replace("embed-", "")]
        self.concurrent_requester = ConcurrentRequester(urls)
        responses = self.concurrent_requester.run_concurrent_requests()

        if None in responses:
            raise Exception("None in responses")
        return responses

    def request_head(self, video_url) -> Response:
        """
        Sends a HEAD request to the provided video URL.

        Args:
            video_url (str): The URL of the video to request.

        Returns:
            Response: The response object from the HEAD request.
        """
        parsed_url = urlparse(video_url)
        return self.concurrent_requester.session.head(
            url=video_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36",
                "Referer": f"{parsed_url.scheme}://{parsed_url.netloc}",
            },
            timeout=20,
        )

    def get_info(self) -> Dict[str, str]:
        """
        Extract video information from the UQLoad URL.

        Returns:
            dict: A dictionary containing extracted video information, including title, video URL,
                  image URL, size, type, resolution, and duration.

        Raises:
            VideoNotFoundError: If the video is not found in the UQLoad URL.
        """

        responses = self.get_responses()

        if None in responses:
            print("None in responses")
            raise

        concatenated_response = f"{responses[0].text}\n{responses[1].text}"

        if (
            concatenated_response.lower().find("file was deleted") > -1
            or concatenated_response.lower().find("file not found") > -1
        ):
            raise VideoNotFoundError("Video not Found")

        video_url = re.search(r"https?://.+/v\.mp4", concatenated_response).group()
        img_url = re.search(r"https?://.*?\.jpg", concatenated_response).group()
        title = re.search(r"title:\s*\"(.*?)\"", concatenated_response).group(1)

        response_head = self.request_head(video_url)
        content_length = int(response_head.headers.get("content-length", 0))
        content_type = response_head.headers.get("content-type")

        self.__video_info.update(
            {
                "title": remove_special_characters(title),
                "video_url": video_url,
                "image_url": img_url,
                "size": content_length,
                "type": content_type,
            }
        )

        h1_tag = re.findall(r"<h1[^>]*>(.*?)</h1>", concatenated_response, re.DOTALL)
        if not len(h1_tag):
            return self.__video_info
        self.__video_info.update(
            {"title": remove_special_characters(" ".join(str(h1_tag[0]).split()))}
        )

        textarea = re.findall(
            r"<textarea[^>]*>(.*?)</textarea>", concatenated_response, re.DOTALL
        )

        resolution_pattern = r"\[(\d+x\d+)\, ((\d+:)*\d+)\]"
        for element in textarea:
            matches = re.search(resolution_pattern, element)
            if matches:
                self.__video_info.update(
                    {"resolution": matches.group(1), "duration": matches.group(2)}
                )
                break

        return self.__video_info
