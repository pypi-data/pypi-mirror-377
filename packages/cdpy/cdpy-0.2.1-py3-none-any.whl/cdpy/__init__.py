from cdpy.launcher import connect  # noqa: E402; noqa: E402

version = "1.0.0"
version_info = tuple(int(i) for i in str(version).split("."))

__all__ = [
    "connect",
    "version",
    "version_info",
]
