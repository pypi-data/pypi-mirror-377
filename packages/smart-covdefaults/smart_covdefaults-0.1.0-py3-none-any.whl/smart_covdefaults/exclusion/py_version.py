import sys


def _all_less_than(version: int, *, inclusive=False) -> str:
    return "|".join(str(x) for x in range(version + inclusive))


def _all_greater_than(version: int, *, inclusive=False) -> str:
    return "|".join(str(x) for x in range(version + inclusive))


def _gen_exclude_for_py_version(major: int, minor: int) -> list[str]:
    # https://github.com/asottile/covdefaults/blob/main/covdefaults.py
    # Copyright (c) 2020 Anthony Sottile
    #
    # Permission is hereby granted, free of charge, to any person obtaining
    # a copy of this software and associated documentation files (the
    # "Software"), to deal in the Software without restriction, including
    # without limitation the rights to use, copy, modify, merge, publish,
    # distribute, sublicense, and/or sell copies of the Software, and to
    # permit persons to whom the Software is furnished to do so, subject to
    # the following conditions:
    #
    # The above copyright notice and this permission notice shall be
    # included in all copies or substantial portions of the Software.
    #
    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    # EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    # MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
    # IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
    # CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
    # TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
    # SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    return [
        fr'# pragma: <=?({_all_less_than(major)})\.\d+ cover\b',
        fr'# pragma: <=?{major}\.({_all_less_than(minor)}) cover\b',
        fr'# pragma: <{major}\.{minor} cover\b',

        fr'# pragma: >=?({_all_greater_than(major)})\.\d+ cover\b',
        fr'# pragma: >=?{major}\.({_all_greater_than(minor)}) cover\b',
        fr'# pragma: >{major}\.{minor} cover\b',

        fr'# pragma: !={major}\.{minor} cover\b',
        fr'# pragma: ==(?!{major}\.{minor} cover)\d+\.\d+ cover\b',
    ]


def exclude_for_py_version() -> list[str]:
    major, minor, *_ = sys.version_info
    return _gen_exclude_for_py_version(major, minor)
