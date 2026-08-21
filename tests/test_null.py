from codemod_yaml import parse_str
from codemod_yaml.items import item, Null


def test_smoke():
    temp = item(None)
    assert isinstance(temp, Null)
    assert temp == None  # noqa: E711
    assert temp.to_string() == "~"
    assert item(None) == item(None)


def test_parse():
    assert parse_str("null")._root == None  # noqa: E711
    assert parse_str("~")._root == None  # noqa: E711


def test_original_spelling_survives_unrelated_edit():
    # Adding a new key forces the whole mapping to re-render (it has no single
    # byte range to splice an insertion into), which used to normalize every
    # sibling null value to "~" regardless of how it was originally spelled.
    stream = parse_str(
        """\
a: null
b: ~
c: Null
d: NULL
"""
    )
    stream["e"] = 1
    assert (
        stream.text
        == b"""\
a: null
b: ~
c: Null
d: NULL
"e": 1
"""
    )


def test_original_spelling_survives_sequence_append():
    stream = parse_str(
        """\
- null
- ~
- Null
"""
    )
    stream.append(1)
    assert (
        stream.text
        == b"""\
- null
- ~
- Null
- 1
"""
    )
