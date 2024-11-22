import logging
from pathlib import Path

import requests

from puddle.exceptions import DownloadError

TIMEOUT = 10

log = logging.getLogger(__name__)


def download(
    url: str, query_parameters: dict | None = None, download_dir: Path | None = None
) -> None:
    try:
        response = requests.get(
            url, stream=True, timeout=TIMEOUT, params=query_parameters
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise DownloadError from e

    log.info(f"Start download from {response.url}")

    try:
        file_name = Path(_get_filename_from_response(response))
    except (IndexError, KeyError):
        file_name = Path(_get_filename_from_url(url))

    if download_dir:
        download_dir.mkdir(parents=True, exist_ok=True)
        file_name = download_dir / file_name

    log.debug(f"File will be saved as {file_name}")
    with file_name.open("wb") as file:
        for chunk in response.iter_content(chunk_size=10 * 1024):
            file.write(chunk)
    log.info(f"Downloaded {file_name}")


def _get_filename_from_url(url: str) -> str:
    fragment_removed = url.split("#")[0]
    query_string_removed = fragment_removed.split("?")[0]
    scheme_removed = query_string_removed.split("://")[-1].split(":")[-1]
    return scheme_removed.split("/")[-1]


def _get_filename_from_response(response: requests.Response) -> str:
    content_disposition = response.headers["content-disposition"]
    return content_disposition.split("filename=")[1]
