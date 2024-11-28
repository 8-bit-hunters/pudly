import logging

from requests.auth import HTTPBasicAuth  # noqa: F401

from .pudly import download, download_files_concurrently  # noqa: F401

logger = logging.getLogger("pudly")
logger.addHandler(logging.NullHandler())
