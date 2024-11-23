from pathlib import Path, PosixPath
from unittest.mock import create_autospec, mock_open, patch

import pytest
import requests

from puddle.exceptions import DownloadError
from puddle.puddle import (
    TIMEOUT_S,
    DownloadedFile,
    _get_filename_from_url,
    download,
)

TEST_URL = "test_url/some_file.txt"


def http_ok_without_content_disposition():
    response = create_autospec(requests.models.Response)
    response.status_code = 200
    response.ok = True
    content = ["chunk1", "chunk2", "chunk3"]
    response.iter_content.return_value = content
    response.url = TEST_URL
    response.headers = {}
    return {"response": response, "content": content}


def http_ok_without_filename():
    response = create_autospec(requests.models.Response)
    response.status_code = 200
    response.ok = True
    content = ["chunk1", "chunk2", "chunk3"]
    response.iter_content.return_value = content
    response.url = TEST_URL
    response.headers = {"content-disposition": "attachment"}
    return {"response": response, "content": content}


def http_ok_with_filename():
    response = create_autospec(requests.models.Response)
    response.status_code = 200
    response.ok = True
    content = ["chunk1", "chunk2", "chunk3"]
    response.iter_content.return_value = content
    response.url = TEST_URL
    response.headers = {"content-disposition": "filename=some_file.txt"}
    return {"response": response, "content": content}


@pytest.mark.parametrize(
    "http_ok_variant",
    [
        pytest.param(
            http_ok_without_content_disposition(), id="without_content_disposition"
        ),
        pytest.param(http_ok_without_filename(), id="without_filename"),
        pytest.param(http_ok_with_filename(), id="with_filename"),
    ],
)
@patch.object(Path, "mkdir")
@patch.object(DownloadedFile, "size_is_correct")
@patch("puddle.puddle.open", new_callable=mock_open)
@patch("puddle.puddle.requests.get")
def test_download_happy_path(request, open, size_is_correct, mkdir, http_ok_variant):
    # Given
    request.return_value = http_ok_variant["response"]
    content = http_ok_variant["content"]
    filename = _get_filename_from_url(TEST_URL)
    size_is_correct.return_value = True

    # When
    result = download(TEST_URL)

    # Then
    request.assert_called_once_with(
        TEST_URL, stream=True, timeout=TIMEOUT_S, params=None
    )
    open.assert_called_once_with(PosixPath(filename), mode="wb")
    for index, chunk in enumerate(content):
        file_handler = open()
        assert file_handler.write.call_args_list[index].args[0] == chunk
    assert result == Path(filename)


@patch.object(Path, "mkdir")
@patch.object(DownloadedFile, "size_is_correct", return_value=True)
@patch("puddle.puddle.open", new_callable=mock_open)
@patch("puddle.puddle.requests.get")
def test_download_with_query_parameters(request, file, size_is_correct, ignore_mkdir):
    # Given
    request.return_value = http_ok_with_filename()["response"]
    query_parameters = {"key": "value"}

    # When
    download(TEST_URL, query_parameters)

    # Then
    request.assert_called_once_with(
        TEST_URL, stream=True, timeout=TIMEOUT_S, params=query_parameters
    )


@patch.object(Path, "mkdir")
@patch.object(DownloadedFile, "size_is_correct", return_value=True)
@patch("puddle.puddle.open", new_callable=mock_open)
@patch("puddle.puddle.requests.get")
def test_download_with_path_option(request, open, size_is_correct, ignore_mkdir):
    # Given
    request.return_value = http_ok_with_filename()["response"]
    download_directory = Path("data")
    filename = _get_filename_from_url(TEST_URL)

    # When
    result = download(TEST_URL, download_dir=download_directory)

    # Then
    open.assert_called_once_with(PosixPath(download_directory / filename), mode="wb")
    assert result == (download_directory / filename)


@patch.object(DownloadedFile, "size_is_correct")
@patch("puddle.puddle.open", new_callable=mock_open)
@patch("puddle.puddle.requests.get")
def test_download_file_size_incorrect(request, file, size_is_correct):
    # Given
    request.return_value = http_ok_with_filename()["response"]
    size_is_correct.return_value = False

    # Then
    with pytest.raises(DownloadError):
        # When
        download(TEST_URL)


@patch("puddle.puddle.open", new_callable=mock_open)
@patch("puddle.puddle.requests.get")
def test_download_exception_during_request(request, file_open):
    # Given
    request.side_effect = requests.exceptions.RequestException
    # Then
    with pytest.raises(DownloadError):
        # When
        download(TEST_URL)

    # Then
    request.assert_called_once_with(
        TEST_URL, stream=True, timeout=TIMEOUT_S, params=None
    )
    file_open.assert_not_called()


def http_file_not_found_response():
    response = create_autospec(requests.models.Response)
    response.status_code = 404
    response.ok = False
    response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    response.headers = None
    return response


def http_authentication_error_response():
    response = create_autospec(requests.models.Response)
    response.status_code = 401
    response.ok = False
    response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    response.headers = None
    return response


@pytest.mark.parametrize(
    "http_error_variant",
    [
        pytest.param(
            http_file_not_found_response(),
            id="file_not_found",
        ),
        pytest.param(
            http_authentication_error_response(),
            id="authentication_error",
        ),
    ],
)
@patch("puddle.puddle.open", new_callable=mock_open)
@patch("puddle.puddle.requests.get")
def test_download_file_with_http_error(request, file_open, http_error_variant):
    # Given
    request.return_value = http_error_variant

    # Then
    with pytest.raises(DownloadError):
        # When
        download(TEST_URL)

    # Then
    request.assert_called_once_with(
        TEST_URL, stream=True, timeout=TIMEOUT_S, params=None
    )
    file_open.assert_not_called()


@pytest.mark.parametrize(
    "url",
    [
        pytest.param("https://a.com/b.pdf?c=d#e", id="url with query and fragment"),
        pytest.param("https://a.com/b.pdf?download=", id="url with query"),
        pytest.param("https://a.com/b.pdf#e", id="url with fragment"),
        pytest.param("https://a.com/b.pdf", id="url only with filename"),
        pytest.param("a.com/download/b.pdf", id="url without scheme"),
    ],
)
def test_get_file_name_from_url(url):
    # When
    result = _get_filename_from_url(url)

    # Then
    assert result == "b.pdf"
