from pathlib import Path
from typing import Any
from unittest.mock import create_autospec, mock_open, patch

import pytest
import requests

from puddle.exceptions import DownloadError
from puddle.puddle import TIMEOUT_S, _get_filename_from_url, download

TEST_URL = "test_url/some_file.txt"


def http_ok_without_content_disposition():
    response = create_autospec(requests.models.Response)
    response.status_code = 200
    response.ok = True
    content = ["chunk1", "chunk2", "chunk3"]
    response.iter_content.return_value = content
    response.url = ""
    response.headers = {}
    return {"response": response, "content": content}


def http_ok_without_filename():
    response = create_autospec(requests.models.Response)
    response.status_code = 200
    response.ok = True
    content = ["chunk1", "chunk2", "chunk3"]
    response.iter_content.return_value = content
    response.url = ""
    response.headers = {"content-disposition": "attachment"}
    return {"response": response, "content": content}


def http_ok_with_filename():
    response = create_autospec(requests.models.Response)
    response.status_code = 200
    response.ok = True
    content = ["chunk1", "chunk2", "chunk3"]
    response.iter_content.return_value = content
    response.url = ""
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
@patch("puddle.puddle._is_file_size_correct", return_value=True)
@patch("puddle.puddle.requests.get")
def test_download_happy_path(request, correct_file_size, http_ok_variant):
    # use a function to mock `open()`,
    # because functions are bound when accessed on instances of `Path`.
    # https://stackoverflow.com/questions/55165313/mock-test-calls-to-path-open
    file_open = mock_open()

    def mocked_open(self, *args, **kwargs):
        return file_open(self, *args, **kwargs)

    def object_called_open() -> str:
        return str(file_open.call_args.args[0])

    def file_open_mode() -> str:
        return file_open.call_args.args[1]

    def file_write_chunk(index: int) -> Any:
        return file_open.return_value.write.call_args_list[index].args[0]

    with patch.object(Path, "open", mocked_open):
        # Given
        request.return_value = http_ok_variant["response"]
        filename = _get_filename_from_url(TEST_URL)
        content = http_ok_variant["content"]

        # When
        result = download(TEST_URL)

    # Then
    request.assert_called_once_with(
        TEST_URL, stream=True, timeout=TIMEOUT_S, params=None
    )
    assert object_called_open() == filename
    assert file_open_mode() == "wb"
    for index, chunk in enumerate(content):
        assert file_write_chunk(index) == chunk
    assert result == Path(filename)


@patch("puddle.puddle._is_file_size_correct", return_value=True)
@patch("puddle.puddle.Path.open", new_callable=mock_open)
@patch("puddle.puddle.requests.get")
def test_download_with_query_parameters(request, file, correct_file_size):
    # Given
    request.return_value = http_ok_with_filename()["response"]
    query_parameters = {"key": "value"}

    # When
    download(TEST_URL, query_parameters)

    # Then
    request.assert_called_once_with(
        TEST_URL, stream=True, timeout=TIMEOUT_S, params=query_parameters
    )


@patch("puddle.puddle._is_file_size_correct", return_value=True)
@patch("puddle.puddle.requests.get")
def test_download_with_path_option(request, correct_file_size):
    # use a function to mock `open()`,
    # because functions are bound when accessed on instances of `Path`.
    # https://stackoverflow.com/questions/55165313/mock-test-calls-to-path-open
    file_open = mock_open()

    def mocked_open(self, *args, **kwargs):
        return file_open(self, *args, **kwargs)

    def object_called_open() -> str:
        return str(file_open.call_args.args[0])

    with patch.object(Path, "open", mocked_open), patch.object(Path, "mkdir"):
        # Given
        request.return_value = http_ok_with_filename()["response"]
        download_directory = Path("data")
        filename = _get_filename_from_url(TEST_URL)

        # When
        result = download(TEST_URL, download_dir=download_directory)

    # Then
    assert object_called_open() == (download_directory / filename).as_posix()
    assert result == (download_directory / filename)


@patch("puddle.puddle._is_file_size_correct")
@patch("puddle.puddle.Path.open", new_callable=mock_open)
@patch("puddle.puddle.requests.get")
def test_download_file_size_incorrect(request, file, is_file_size_correct):
    # Given
    request.return_value = http_ok_with_filename()["response"]
    is_file_size_correct.return_value = False

    # Then
    with pytest.raises(DownloadError):
        # When
        download(TEST_URL)


@patch("puddle.puddle.open", new_callable=mock_open)
@patch("puddle.puddle.requests.get", side_effect=requests.exceptions.RequestException)
def test_download_exception_during_request(request, file_open):
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
