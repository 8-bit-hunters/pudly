import pytest
import requests

from pudly.pudly import download

URL = "https://api.worldbank.org/v2/en/indicator/NY.GDP.MKTP.CD"
QUERY_PARAMETERS = {"downloadformat": "csv"}


@pytest.fixture
def get_package_info():
    response = requests.get(URL, stream=True, timeout=10, params=QUERY_PARAMETERS)

    name = response.headers["content-disposition"].split("filename=")[1]
    size = int(response.headers["content-length"])

    return {
        "name": name,
        "size": size,
    }


def test_download_file_from_wordbank(tmp_path, get_package_info):
    # Given
    name = get_package_info["name"]
    size = get_package_info["size"]

    # When
    download(URL, download_dir=tmp_path, query_parameters=QUERY_PARAMETERS)

    # Then
    expected_path = tmp_path / name
    assert expected_path.exists()
    assert expected_path.stat().st_size == size
