import importlib.metadata

from cdpy.launcher import connect  # noqa: E402; noqa: E402

version = importlib.metadata.version("cdpy")
version_info = tuple(int(i) for i in str(version).split("."))

__all__ = [
    "connect",
    "version",
    "version_info",
]
