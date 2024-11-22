from unittest.mock import create_autospec, mock_open, patch

import pytest
import requests

from puddle.exceptions import DownloadError
from puddle.puddle import TIMEOUT, download, get_filename_from_url

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
    "http_ok",
    [
        pytest.param(
            http_ok_without_content_disposition(), id="without_content_disposition"
        ),
        pytest.param(http_ok_without_filename(), id="without_filename"),
        pytest.param(http_ok_with_filename(), id="with_filename"),
    ],
)
@patch("puddle.puddle.open", new_callable=mock_open)
@patch("puddle.puddle.requests.get")
def test_download_happy_path(mocked_get, mocked_open, http_ok):
    # Given
    mocked_get.return_value = http_ok["response"]
    filename = get_filename_from_url(TEST_URL)
    content = http_ok["content"]

    # When
    download(TEST_URL)

    # Then
    mocked_get.assert_called_once_with(
        TEST_URL, stream=True, timeout=TIMEOUT, params=None
    )
    mocked_open.assert_called_once_with(filename, mode="wb")
    for index, chunk in enumerate(content):
        assert mocked_open().write.call_args_list[index].args[0] == chunk


@patch("puddle.puddle.open", new_callable=mock_open)
@patch("puddle.puddle.requests.get")
def test_download_with_query_paramters(mocked_get, mocked_open):
    # Given
    mocked_get.return_value = http_ok_with_filename()["response"]
    query_paramters = {"key": "value"}

    # When
    download(TEST_URL, query_paramters)

    # Then
    mocked_get.assert_called_once_with(
        TEST_URL, stream=True, timeout=TIMEOUT, params=query_paramters
    )


@patch("puddle.puddle.open", new_callable=mock_open)
@patch("puddle.puddle.requests.get", side_effect=requests.exceptions.RequestException)
def test_download_exception_during_request(mocked_get, mocked_open):
    with pytest.raises(DownloadError):
        # When
        download(TEST_URL)

    # Then
    mocked_get.assert_called_once_with(
        TEST_URL, stream=True, timeout=TIMEOUT, params=None
    )
    mocked_open.assert_not_called()


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
    "http_response",
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
def test_download_file_with_http_error(mocked_get, mocked_open, http_response):
    # Given
    mocked_get.return_value = http_response
    with pytest.raises(DownloadError):
        # When
        download(TEST_URL)

    # Then
    mocked_get.assert_called_once_with(
        TEST_URL, stream=True, timeout=TIMEOUT, params=None
    )
    mocked_open.assert_not_called()


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
def test_download_auto_file_naming(url):
    # When
    result = get_filename_from_url(url)

    # Then
    assert result == "b.pdf"
