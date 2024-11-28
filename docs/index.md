# Python Url Downloader Library 🤷

PUDLy is yet another URL downloader for python.

## Goal of the project

The goal of this project is to create simple functions to handle file download tasks.

The two main components of this library are:

- [`download()`](http://127.0.0.1:8000/references/#pudly.pudly.download)
- [`download_files_concurrently()`](http://127.0.0.1:8000/references/#pudly.pudly.download_files_concurrently)

## How to use

### Downloading one file

The `download` function can be used to download a file from an url. The function returns the downloaded file's path as
`Path`.

```python
from pudly import download

url = "https://databank.worldbank.org/data/download/WDI_CSV.zip"
file = download(url)

assert file.exists()
```

It takes optional arguments to specify the download directory or any query parameters for the request.

```python
from pudly import download
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
from pudly import download_files_concurrently

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

!!! note

    `download_dir` and `query_parameters` arguments are used for every URL in the list when downloaded.

## Exception Handling

The library has custom exception type called `DownloadError`. Errors from `requests` are caught and raised as
`DownloadError`.

The downloaded file is validated at the end of the process by comparing the expected size with the actual one. If the
sizes are mismatched then `DownloadError` will be raised.

## Logging

The library uses the python logging library. The name of the logger is `pudly` and can be accessed by importing it or
calling the `logging.getLogger()` function.

### Importing

```python
from pudly import logger as pudly_logger
```

### getLogger

```python
import logging
pudly_logger = logging.getLogger("pudly")
```

### Configuration

If you want to enable the logging for the library, you can add a handler to the `log` logger as in the following
example.

```python
import logging
from pudly import download
from pudly import logger as pudly_logger

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
formatter = logging.Formatter(log_format)

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(formatter)

pudly_logger.addHandler(console)
pudly_logger.setLevel(logging.DEBUG)

download("https://api.worldbank.org/v2/en/indicator/NY.GDP.MKTP.CD?downloadformat=csv")
```

Output on console:

```shell
2024-11-23 17:14:21,992 - pudly - INFO - Download from https://api.worldbank.org/v2/en/indicator/NY.GDP.MKTP.CD?downloadformat=csv (135117 bytes)
2024-11-23 17:14:21,992 - pudly - DEBUG - Start downloading API_NY.GDP.MKTP.CD_DS2_en_csv_v2_2.zip
2024-11-23 17:14:22,019 - pudly - DEBUG - API_NY.GDP.MKTP.CD_DS2_en_csv_v2_2.zip downloaded 135117 bytes / 135117 bytes
2024-11-23 17:14:22,019 - pudly - DEBUG - Finished downloading API_NY.GDP.MKTP.CD_DS2_en_csv_v2_2.zip
2024-11-23 17:14:22,020 - pudly - INFO - Downloaded API_NY.GDP.MKTP.CD_DS2_en_csv_v2_2.zip successfully
```
