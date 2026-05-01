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
    :\Z    | # colon at end of string becomes a mapping value indicator
    [ ]\#  | # space+hash starts a comment, truncating the scalar
    ^,     | # separator
    ^!     | # tag
    ^\#    | # comment
    ^&     | # anchor
    ^\*    | # alias
    ^%     | # directive
    ^[|>]  | # block scalar
    ^@     | # reserved
    ^[\[\]] | # flow sequence
    ^`     | # reserved
    ^[{}]  | # map
    ^-(?:[ \n]|\Z)    | # seq
    [\r\n] | # multiline
    ^(?:null|Null|NULL|~)\b | # null (tree-sitter accepts all three cases)
    ^0x[0-9a-fA-F]+\b | # hex
    ^0b[01]+\b        | # bin
    ^0o[0-7]+\b       | # oct (some parsers still accept, we won't output)
    ^(?:true|false|True|False|TRUE|FALSE)\b | # bool (case variants)
    ^[+-]?\.(?:inf|Inf|INF)\b | # float infinity
    ^\.(?:nan|NaN|NAN)\b      | # float NaN
    ^[+-]?(?:\.[0-9]+|[0-9]+(?:\.[0-9]*)?)(?:[eE][+-]?[0-9]+)?\Z # floats
""",
    re.X,
)

DQ_ESCAPE_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e\t\r\n-\x1f\"\\\x7f-\xff]")
SQ_ESCAPE_RE = re.compile(r"'")
SQ_INVALID_RE = re.compile(r"[\x00-\x1f\x7f-\x9f]")  # including \n
PLAIN_INVALID_RE = re.compile(r"[\x00-\x1f\'\"~\x7f-\x9f]")

PRETTY_ESCAPES = {
    "\\": "\\",
    '"': '"',
    "/": "/",
    "t": "\t",
    "a": "\a",
    "b": "\b",
    "e": "\x1b",
    "f": "\f",
    "v": "\v",
    "n": "\n",
    "r": "\r",
    " ": " ",
    "N": "\x85",
    "_": "\xa0",
    "L": " ",
    "P": " ",
}
REV_PRETTY_ESCAPES = {v: k for k, v in PRETTY_ESCAPES.items()}
# \\[\n\r][ \t]* must come before \\[^uUx] so the line-continuation case
# (backslash + actual newline) is absorbed together with its trailing indent.
ESCAPE_RE = re.compile(
    r"\\U[0-9a-fA-F]{8}"
    r"|\\u[0-9a-fA-F]{4}"
    r"|\\x[0-9a-fA-F]{2}"
    r"|\\[\n\r][ \t]*"
    r"|\\[^uUx]"
)


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
    elif g[1] in "uUx":
        return chr(int(g[2:], 16))
    elif g[1] in "\n\r":
        # \<newline> is a line-continuation: the backslash, the newline, and any
        # leading whitespace on the next line are all discarded.
        return ""
    else:
        # \0
        return chr(int(g[1:]))


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
    if not x:
        return None
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


# Line-break characters recognised by pyyaml (YAML 1.1 compatible):
# LF, CR, NEL (U+0085), LS (U+2028), PS (U+2029).
_YAML_LB = "\n\r\x85  "

# Matches a run of whitespace that contains at least one line-break — the unit
# that YAML flow-scalar line-folding collapses.
_SQ_FOLD_RE = re.compile(r"[ \t]*(?:[" + _YAML_LB + r"][ \t]*)+")


def _fold_newline(m: re.Match[str]) -> str:
    n = sum(1 for c in m.group(0) if c in _YAML_LB)
    return " " if n == 1 else "\n" * (n - 1)


def unescape_sq(x: str) -> str:
    """Decode a raw single-quoted YAML scalar (including the surrounding quotes)."""
    raw = x[1:-1]
    # Apply flow-scalar line folding before un-doubling quotes.
    return _SQ_FOLD_RE.sub(_fold_newline, raw).replace("''", "'")


def fold_plain(x: str) -> str:
    """Apply YAML flow line folding to a plain scalar that may span multiple lines."""
    return _SQ_FOLD_RE.sub(_fold_newline, x)
