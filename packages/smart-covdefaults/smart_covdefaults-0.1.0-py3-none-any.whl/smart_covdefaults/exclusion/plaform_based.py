import os
import sys
from typing import Final

_PLATFORM_TAGS: Final = frozenset((
    "nt", "posix",
    "cygwin", "darwin", "linux", "msys", "win32",
    "cpython", "mypy"
))


def _gen_for_platform(current_tags: set[str]) -> list[str]:
    return [
        fr"# pragma: {inactive_tag} cover\b"
        for inactive_tag in _PLATFORM_TAGS.difference(current_tags)
    ] + [
        fr"# pragma: {active_tag} no cover\b"
        for active_tag in current_tags
    ]


def _get_current_tags() -> set[str]:
    return {os.name, sys.platform, sys.implementation.name}


def exclude_for_platform() -> list[str]:
    return _gen_for_platform(_get_current_tags())
