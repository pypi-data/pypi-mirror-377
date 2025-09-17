import os
import sys

IS_WINDOWS = sys.platform == "win32"
_BASE_PATH = "X:\\" if IS_WINDOWS else "/data"


def make_path(*parts) -> str:
    return os.path.join(_BASE_PATH, *parts)
