from __future__ import annotations

from typing import Optional
import re

NON_STRING_RE = re.compile(
    r"""
    ^\s+   | # leading whitespace
    \s+$   | # trailing whitespace
    ^\?    | # explicit key
    ^:     | # explicit value
    :[ ]   | # colon-space looks like a map key
    ^,     | # separator
    ^!     | # tag
    ^\#    | # comment
    ^&     | # ??
    ^\*    | # ??
    ^%     | # ??
    ^[|>]  | # str
    ^@     | # ??
    ^[\[\]] | # seq
    ^`     | # ??
    ^[{}]  | # map
    ^-(?:[ \n]|\Z)    | # seq
    [\r\n] | # multiline
    ^(?:null|~)\b     | # null
    ^0x[0-9a-fA-F]+\b | # hex
    ^0b[01]\b         | # bin
    ^0o[0-7]\b        | # oct (some parsers still accept, we won't output)
    ^(true|false)\b  | # bool
    ^-?(?:[0-9]+\.)?[0-9]+(?:[eE][0-9]+)?\Z # floats
""",
    re.X,
)

DQ_ESCAPE_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e\t\r\n-\x1f\"\\\x7f-\xff]")
SQ_ESCAPE_RE = re.compile(r"'")
SQ_INVALID_RE = re.compile(r"[\x00-\x1f]")  # including \n
PLAIN_INVALID_RE = re.compile(r"[\x00-\x1f\'\"~\x7f-\x9f]")

PRETTY_ESCAPES = {
    "\\": "\\",
    '"': '"',
    "t": "\t",
    "n": "\n",
    "r": "\r",
    "_": "\xa0",
}
REV_PRETTY_ESCAPES = {v: k for k, v in PRETTY_ESCAPES.items()}
ESCAPE_RE = re.compile(r"\\u[0-9a-fA-F]{4}|\\x[0-9a-fA-F]{2}|\\[^ux]")


def _add_backslash(m: re.Match[str]) -> str:
    g = m.group(0)
    if g in REV_PRETTY_ESCAPES:
        return "\\" + REV_PRETTY_ESCAPES[g]

    n = ord(m.group(0))
    if n < 256:
        return "\\x%02x" % (n,)
    else:
        # We don't need long unicode escapes because they won't match the regex
        return "\\u%04x" % (n,)


def _unescape(m: re.Match[str]) -> str:
    g = m.group(0)
    if g[1] in PRETTY_ESCAPES:
        return PRETTY_ESCAPES[g[1]]
    elif g[1] in "ux":
        return chr(int(g[2:], 16))
    else:
        # ??? TODO
        return g[1:]


def _double_up_sq(m: re.Match[str]) -> str:
    return m.group(0) + m.group(0)


# The most correct way to do this would be with reparsing and checking
# the tree-sitter type, but this is _much_ faster.  Note that plain strings
# don't allow any escapes.


def safe_plain_repr(x: str, validate: bool = True) -> Optional[str]:
    """
    Returns a minimal plain string that should evaluate to `x`.

    Returns None if it would be confused with some other type.
    """
    if validate:
        if NON_STRING_RE.search(x):
            return None
        if PLAIN_INVALID_RE.search(x):
            return None
    return x


def safe_dq_repr(x: str) -> Optional[str]:
    """
    Returns a minimal double quoted string that should evaluate to `x`.
    """
    return '"' + DQ_ESCAPE_RE.sub(_add_backslash, x) + '"'


def unescape_dq(x: str) -> str:
    return ESCAPE_RE.sub(_unescape, x[1:-1])


def safe_sq_repr(x: str) -> Optional[str]:
    if SQ_INVALID_RE.search(x):
        return None
    return "'" + SQ_ESCAPE_RE.sub(_double_up_sq, x) + "'"
