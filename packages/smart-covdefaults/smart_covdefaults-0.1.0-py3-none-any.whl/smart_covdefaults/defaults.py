from types import MappingProxyType
from typing import Final

DEFAULT_OPTIONS: Final = MappingProxyType({
    "report:show_missing": True,
    "report:skip_covered": True
})

DEFAULT_EXCLUSION: Final = (
    # a more strict default pragma
    r'# pragma: no cover\b',
    # allow defensive code
    r'^\s*raise AssertionError\b',
    r'^\s*raise NotImplementedError\b',
    r'^\s*return NotImplemented\b',
    r'^\s*raise$',
    # typing-related code
    r'^\s*if (False|TYPE_CHECKING):',
    r': \.\.\.(\s*#.*)?$',
    r'^ +\.\.\.$',
    r'-> [\'"]?NoReturn[\'"]?:',
    r'^\s*assert_never\b',
    # non-runnable code
    r'^if __name__ == [\'"]__main__[\'"]:$',
)
