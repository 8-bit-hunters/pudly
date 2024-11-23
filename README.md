# P.U.D.L.y

Python Url Downloader Library 🤷

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/8-bit-hunters/puddle/main.svg)](https://results.pre-commit.ci/latest/github/8-bit-hunters/puddle/main)
[![pytest](https://github.com/8-bit-hunters/pudly/actions/workflows/testing.yaml/badge.svg)](https://github.com/8-bit-hunters/pudly/actions/workflows/testing.yaml)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![gitmoji](https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg?style=flat-square)](https://gitmoji.dev/)

The goal of this library to create easy to use functions to download files in Python.

- [Pypi](https://pypi.org/project/pudly/)
- [Github](https://github.com/8-bit-hunters/pudly)
- [Documentation](https://8-bit-hunters.github.io/pudly/)

## Examples

### Downloading one file

The `download` function can be used to download a file from an url. The function returns the downloaded file's path.

```python
from pudly.pudly import download

url = "https://databank.worldbank.org/data/download/WDI_CSV.zip"
file = download(url)

assert file.exists()
```

It takes optional arguments to specify the download directory or any query parameters for the request.

```python
from pudly.pudly import download
from pathlib import Path

url = "https://api.worldbank.org/v2/en/indicator/NY.GDP.MKTP.CD"
query_parameters = {"downloadformat": "csv"}
download_directory = Path("data")

file = download(url, download_dir=download_directory, query_parameters=query_parameters)

assert file.exists()
```

### Downloading multiple files

The `download_files_concurrently` function uses threading to download files in parallel. It returns the list of the
downloaded file's path.

```python
from pathlib import Path
from pudly.pudly import download_files_concurrently

urls = [
    "https://api.worldbank.org/v2/en/indicator/SP.POP.TOTL?downloadformat=csv",
    "https://api.worldbank.org/v2/en/indicator/NY.GDP.MKTP.CD?downloadformat=csv",
    "https://api.worldbank.org/v2/en/indicator/EN.POP.DNST?downloadformat=csv",
]
download_dictionary = Path("data")

files = download_files_concurrently(urls, download_dir=download_dictionary)

for file in files:
    assert file.exists()
```
