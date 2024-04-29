import os
from PyQt5.QtCore import QSettings

settings = QSettings("VideoDownloader", "uqload downloader gui")


def get_config() -> QSettings:
    """
    Retrieves the configuration settings.

    If certain settings are not already set, default values are applied:
    - 'output_dir': Current working directory.
    - 'max_queue': 10.
    - 'concurrent_downloads': 2.

    Returns:
        QSettings: A QSettings object containing the configuration settings.
    """
    if settings.value("output_dir") is None:
        settings.setValue("output_dir", os.path.normpath(os.getcwd()))
    if settings.value("max_queue") is None:
        settings.setValue("max_queue", 10)
    if settings.value("concurrent_downloads") is None:
        settings.setValue("concurrent_downloads", 2)

    return settings
