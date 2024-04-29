import requests
from threading import Thread
from typing import List, Union


class ConcurrentRequester:
    """Performs parallel requests..

    Performs parallel requests from a given list of urls.

    Attributes:
        urls (List[str]): A list of URLs to fetch.
        session (requests.Session): A requests Session object used for making requests.
        responses (List[Tuple[int, Union[requests.Response, None]]]):
        A list of tuples containing the index of the URL in the input list and the
        corresponding response object or None if the request failed.
    """

    def __init__(self, urls: List[str]) -> None:
        """
        Initializes a ConcurrentRequester object.

        Args:
            urls (List[str]): A list of URLs to fetch.
        """
        self.urls = self.__validate_urls(urls)
        self.session = requests.Session()
        self.responses = []

    def __validate_urls(self, urls: List[str]) -> List[str]:
        """
        Validates the provided list of URLs.

        Args:
            urls (List[str]): A list of URLs to validate.

        Returns:
            List[str]: The validated list of URLs.

        Raises:
            ValueError: If the provided URLs are not a non-empty list.
        """
        if not isinstance(urls, list) or not len(urls):
            raise ValueError("urls must be a non-empty list")
        return urls

    def fetch_url(self, url: str, idx: int) -> None:
        """
        This method prints a message indicating the start of the request for the URL,
        fetches the URL using the requests library, and stores the response or None if the request fails
        in the `responses` attribute.

        Args:
            url (str): The URL to fetch.
            idx (int): The index of the URL in the input list.
        """
        response = self.session.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            },
        )
        if response.status_code == 200:
            self.responses.append((idx, response))
            return
        self.responses.append((idx, None))

    def run_concurrent_requests(self) -> List[Union[requests.Response, None]]:
        """
        Fetches all URLs concurrently and returns the responses.

        This method creates a list of threads, one for each URL. Each thread calls the `fetch_url`
        method to fetch the corresponding URL. The method then waits for all threads to finish
        and returns a list of responses sorted by the order of the URLs in the input list.

        Returns:
            List[Union[requests.Response, None]]:
            A list of responses or None objects corresponding to the URLs.
        """
        __thread_list: List[Thread] = []

        for idx, url in enumerate(self.urls):
            __thread = Thread(target=self.fetch_url, args=(url, idx))
            __thread_list.append(__thread)
            __thread.start()

        for __thread in __thread_list:
            __thread.join()

        return [response for _, response in sorted(self.responses)]
