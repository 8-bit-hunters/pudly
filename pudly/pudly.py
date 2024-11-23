import concurrent
import logging
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path

import requests

from pudly.exceptions import DownloadError

DOWNLOAD_CHUNK_MB = 25
TIMEOUT_S = 10
MEGABYTE_TO_BYTES = 1024 * 1024

log = logging.getLogger(__name__)


class DownloadedFile:
    def __init__(self, path: Path, total_size: int) -> None:
        self._path = path
        self._total_size = total_size

    @property
    def path(self) -> Path:
        return self._path

    def total_size_in_bytes(self) -> int:
        return self._total_size

    def size_is_correct(self) -> bool:
        return self.path.stat().st_size == self._total_size


class FileToDownload:
    def __init__(self, response: requests.Response) -> None:
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
        self._download_dir.mkdir(parents=True, exist_ok=True)
        full_path = self._download_dir / self._name
        with open(full_path, mode="wb") as f:  # noqa: PTH123
            downloaded_size = 0
            log.debug(f"Start downloading {self.name}")
            for chunk in self._connection.iter_content(chunk_size=download_chunk_size):
                downloaded_size += len(chunk)
                log.debug(
                    f"{self._name} downloaded {downloaded_size} bytes"
                    f" / {self._total_size} bytes"
                )
                f.write(chunk)
        log.debug(f"Finished downloading {self.name}")
        return DownloadedFile(full_path, self._total_size)

    def _get_name(self) -> Path:
        try:
            name = _get_filename_from_response(self._connection)
        except (KeyError, IndexError):
            name = _get_filename_from_url(self._url)
        return Path(name)


def download(
    url: str, query_parameters: dict | None = None, download_dir: Path | None = None
) -> Path:
    try:
        response = requests.get(
            url, stream=True, timeout=TIMEOUT_S, params=query_parameters
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise DownloadError from e

    file = FileToDownload(response)

    log.info(f"Download from {file.url} ({file.total_size_in_bytes} bytes)")

    if download_dir:
        file.download_dir = download_dir

    downloaded_file = file.download(DOWNLOAD_CHUNK_MB * MEGABYTE_TO_BYTES)

    if not downloaded_file.size_is_correct():
        message = f"File size corrupted for {downloaded_file.path}"
        raise DownloadError(message)

    log.info(f"Downloaded {downloaded_file.path.name} successfully")

    return downloaded_file.path


def download_files_concurrently(
    url_list: list[str],
    query_parameters: dict | None = None,
    download_dir: Path | None = None,
    max_workers: int = 5,
) -> list[Path]:
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                download,
                url,
                query_parameters=query_parameters,
                download_dir=download_dir,
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
