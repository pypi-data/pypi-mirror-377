import functools
from dataclasses import dataclass


@functools.total_ordering
@dataclass(frozen=True, slots=True)
class Version:
    major: int
    minor: int

    def __lt__(self, other: "Version | float | str | Any") -> bool:
        if isinstance(other, Version):
            return (
                self.major < other.major
                or self.major == other.major and self.minor < other.minor
            )
        if isinstance(other, float) or isinstance(other, str):
            converted = _to_ver(str(other))
            if not converted:
                return NotImplemented
            return self < converted
        return NotImplemented

    def __eq__(self, other: "Version | float | str | Any") -> bool:
        if isinstance(other, Version):
            return self.major == other.major and self.minor == other.minor
        if isinstance(other, float) or isinstance(other, str):
            converted = _to_ver(str(other))
            if not converted:
                return NotImplemented
            return self == converted
        return NotImplemented


def _to_ver(ver_string: str) -> Version | None:
    try:
        major, minor = map(int, ver_string.split("."))
        return Version(major, minor)
    except ValueError:
        return None
