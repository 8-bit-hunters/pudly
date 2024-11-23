import logging
from pathlib import Path

import requests

from puddle.exceptions import DownloadError

DOWNLOAD_CHUNK_MB = 25
TIMEOUT_S = 10
MEGABYTE_TO_BYTES = 1024 * 1024

log = logging.getLogger(__name__)


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

    total_size = int(response.headers.get("content-length", 0))

    log.info(f"Start download from {response.url} ({total_size} bytes)")

    try:
        file_name = Path(_get_filename_from_response(response))
    except (IndexError, KeyError):
        file_name = Path(_get_filename_from_url(url))

    if download_dir:
        download_dir.mkdir(parents=True, exist_ok=True)
        file_name = download_dir / file_name

    log.debug(f"File will be saved as {file_name}")
    with file_name.open("wb") as file:
        downloaded_size = 0
        for chunk in response.iter_content(
            chunk_size=DOWNLOAD_CHUNK_MB * MEGABYTE_TO_BYTES
        ):
            downloaded_size += len(chunk)
            log.debug(f"Downloaded {downloaded_size} Bytes / {total_size} Bytes")
            file.write(chunk)

    if not _is_file_size_correct(file_name, total_size):
        message = "File size corrupted"
        raise DownloadError(message)

    log.info(f"Downloaded {file_name}")
    return Path(file_name)


def _get_filename_from_url(url: str) -> str:
    fragment_removed = url.split("#")[0]
    query_string_removed = fragment_removed.split("?")[0]
    scheme_removed = query_string_removed.split("://")[-1].split(":")[-1]
    return scheme_removed.split("/")[-1]


def _get_filename_from_response(response: requests.Response) -> str:
    content_disposition = response.headers["content-disposition"]
    return content_disposition.split("filename=")[1]


def _is_file_size_correct(file: Path, size: int) -> bool:
    return file.stat().st_size == size
