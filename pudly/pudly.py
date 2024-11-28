import concurrent
import logging
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

from pudly.exceptions import DownloadError

DOWNLOAD_CHUNK_MB = 25
TIMEOUT_S = 10
MEGABYTE_TO_BYTES = 1024 * 1024

logger = logging.getLogger("pudly")


class DownloadedFile:
    """
    Represents a file downloaded from a URL.
    """

    def __init__(self, path: Path, total_size: int) -> None:
        """
        Initialise a DownloadedFile object.

        Args:
            path: The path of the downloaded file.
            total_size: The total size of the downloaded file from download information.
        """
        self._path = path
        self._total_size = total_size

    @property
    def path(self) -> Path:
        return self._path

    def total_size_in_bytes(self) -> int:
        """
        Return the total size in bytes according to download information.

        Returns:
            The total size in bytes.
        """
        return self._total_size

    def size_is_correct(self) -> bool:
        """
        Compare the size of the file to the total size according to
        download information.

        Returns:
             True if the size is correct, False otherwise.
        """
        return self.path.stat().st_size == self._total_size


class FileToDownload:
    """
    Represents a file to be downloaded from a URL.
    """

    def __init__(self, response: requests.Response) -> None:
        """
        Initialise a FileToDownload object

        Args:
            response: The response object from the requests to a URL.
        """
        self._total_size = int(response.headers.get("content-length", 0))
        self._connection = response
        self._url = self._connection.url
        self._download_dir = Path()
        self._name = self._get_name()

    @property
    def total_size_in_bytes(self) -> int:
        return self._total_size

    @property
    def url(self) -> str:
        return self._url

    @property
    def name(self) -> Path:
        return self._name

    @property
    def download_dir(self) -> Path:
        return self._download_dir

    @download_dir.setter
    def download_dir(self, path: Path) -> None:
        self._download_dir = path

    def download(self, download_chunk_size: int) -> DownloadedFile:
        """
        Download the file from the URL.

        Args:
            download_chunk_size: The size of a fragment in bytes during download.

        Returns:
             The downloaded file object.
        """
        self._download_dir.mkdir(parents=True, exist_ok=True)
        full_path = self._download_dir / self._name
        with open(full_path, mode="wb") as f:  # noqa: PTH123
            downloaded_size = 0
            logger.debug(f"Start downloading {self.name}")
            for chunk in self._connection.iter_content(chunk_size=download_chunk_size):
                downloaded_size += len(chunk)
                logger.debug(
                    f"{self._name} downloaded {downloaded_size} bytes"
                    f" / {self._total_size} bytes"
                )
                f.write(chunk)
        logger.debug(f"Finished downloading {self.name}")
        return DownloadedFile(full_path, self._total_size)

    def _get_name(self) -> Path:
        try:
            name = _get_filename_from_response(self._connection)
        except (KeyError, IndexError):
            name = _get_filename_from_url(self._url)
        return Path(name)


def download(
    url: str,
    query_parameters: dict | None = None,
    download_dir: Path | None = None,
    auth: HTTPBasicAuth | None = None,
) -> Path:
    """
    Download the file from the URL.

    Args:
        url: The URL to download from.
        query_parameters: Parameters to pass to the URL.
        download_dir: The directory to download the file to.

    Returns:
         The path of the downloaded file.

    Raises:
        DownloadError: If the download fails.
    """
    try:
        response = requests.get(
            url, stream=True, timeout=TIMEOUT_S, params=query_parameters, auth=auth
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise DownloadError from e

    file = FileToDownload(response)

    logger.info(f"Download from {file.url} ({file.total_size_in_bytes} bytes)")

    if download_dir:
        file.download_dir = download_dir

    downloaded_file = file.download(DOWNLOAD_CHUNK_MB * MEGABYTE_TO_BYTES)

    if not downloaded_file.size_is_correct():
        message = f"File size corrupted for {downloaded_file.path}"
        raise DownloadError(message)

    logger.info(f"Downloaded {downloaded_file.path.name} successfully")

    return downloaded_file.path


def download_files_concurrently(
    url_list: list[str],
    query_parameters: dict | None = None,
    download_dir: Path | None = None,
    auth: HTTPBasicAuth | None = None,
    max_workers: int = 5,
) -> list[Path]:
    """
    Download files from a list of URLs.

    Args:
        url_list: The list of URLs to download.
        query_parameters: The parameters to pass to the URLs.
        download_dir: The directory to download the files to.
        max_workers: The maximum number of concurrent downloads.

    Returns:
         The list of paths to the downloaded files.
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                download,
                url,
                query_parameters=query_parameters,
                download_dir=download_dir,
                auth=auth,
            )
            for url in url_list
        ]

    return [future.result() for future in concurrent.futures.as_completed(futures)]


def _get_filename_from_url(url: str) -> str:
    fragment_removed = url.split("#")[0]
    query_string_removed = fragment_removed.split("?")[0]
    scheme_removed = query_string_removed.split("://")[-1].split(":")[-1]
    return scheme_removed.split("/")[-1]


def _get_filename_from_response(response: requests.Response) -> str:
    content_disposition = response.headers["content-disposition"]
    return content_disposition.split("filename=")[1]
