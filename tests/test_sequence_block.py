from codemod_yaml import parse_str
from codemod_yaml.items import String, QuoteStyle


def test_simple_sequence():
    stream = parse_str("- foo\n- bar\n")

    # Simple invariant, we should return the exact same object
    first = stream[0]
    second = stream[0]
    assert first is second

    assert stream[0] == "foo"
    assert stream[1] == "bar"
    # didn't make any edits, this should be fine
    assert stream.text == b"- foo\n- bar\n"


def test_edit_sequence():
    stream = parse_str("- foo\n- bar\n")
    stream.append(String("baz", QuoteStyle.BARE))
    assert stream.text == b"- foo\n- bar\n- baz\n"
    stream.append(String("zab", QuoteStyle.BARE))
    assert stream.text == b"- foo\n- bar\n- baz\n- zab\n"


def test_edit_sequence2():
    stream = parse_str("- foo\n- bar\n- baz\n")
    del stream[1]
    assert stream.text == b"- foo\n- baz\n"
    stream.append(String("zab", QuoteStyle.BARE))
    assert stream.text == b"- foo\n- baz\n- zab\n"


def test_int_sequence():
    stream = parse_str("- 1\n- 0xff\n")
    assert stream[0] == 1
    assert stream[1] == 255
    # didn't make any edits, this should be fine
    assert stream.text == b"- 1\n- 0xff\n"


def test_string_sequence():
    stream = parse_str("""\
- a
- "b"
- 'c'
- |
  d
""")
    assert stream[0] == "a"
    assert stream[1] == "b"
    assert stream[2] == "c"
    # TODO actually an xfail
    assert stream[3] == "d"
    # didn't make any edits, this should be fine
    assert stream.text == b"- a\n- \"b\"\n- 'c'\n- |\n  d\n"
    stream[3] = "x"
    assert stream.text == b'- a\n- "b"\n- \'c\'\n- "x"\n'


def test_nested_sequence():
    stream = parse_str("""\
-
  -  a
  -  b
  -  c
""")
    assert stream[0][0] == "a"
    assert stream[0][1] == "b"
    assert stream[0][2] == "c"
    # didn't make any edits, this should be fine
    assert stream.text == b"-\n  -  a\n  -  b\n  -  c\n"
    stream[0][1] = String("new", QuoteStyle.BARE)
    assert (
        stream.text
        == b"""\
-
  -  a
  -  new
  -  c
"""
    )
    del stream[0][1]
    assert stream.text == b"-\n  -  a\n  -  c\n"
    stream[0].append(String("d", QuoteStyle.BARE))
    assert stream.text == b"-\n  -  a\n  -  c\n  -  d\n"


def test_slicing():
    stream = parse_str("""\
-
  -  a
  -  b
  -  c
  -  d
""")
    assert stream[0][0:2] == ["a", "b"]
    assert stream[0][1:3] == ["b", "c"]
    assert stream[0][1:] == ["b", "c", "d"]
    assert stream[0][:2] == ["a", "b"]
    assert stream[0][0:3:2] == ["a", "c"]
    assert stream[0][1:3:2] == ["b"]
    assert stream[0][1::2] == ["b", "d"]
    assert stream[0][1:3:1] == ["b", "c"]


def test_slicing_modification():
    stream = parse_str("""\
-
    -   a
""")
    stream[0][:] = [String("b", QuoteStyle.BARE), String("c", QuoteStyle.BARE)]
    assert (
        stream.text
        == b"""\
-
    -   b
    -   c
"""
    )


def test_combo_modification():
    stream = parse_str("""\
a:
 - 1
 - 2

b:
""")
    # tree-sitter appears to give the sequence all the trailing newlines UNLESS
    # followed by a map key, in which case nobody gets them.
    stream["a"][:] = [3, 4, 5]
    assert (
        stream.text
        == b"""\
a:
 - 3
 - 4
 - 5

b:
"""
    )


def test_cookie_sequence():
    stream = parse_str("""\
- a
""")
    stream.append("b")
    del stream[1]
    assert stream.text == b"- a\n"


def test_nested():
    stream = parse_str("""\
-
 - a
 - b
""")
    stream[0].extend(("c", "d"))
    assert stream.text == b'-\n - a\n - b\n - "c"\n - "d"\n'


def test_same_line_nested():
    stream = parse_str("""\
- - x
  - y
""")
    stream[0][0] = "z"
    assert (
        stream.text
        == b"""\
-
  - "z"
  - y
"""
    )


def test_same_line_triple_nested():
    stream = parse_str("""\
- - - x
    - y
  - - z
""")
    stream[0][0][0] = "mmm"
    assert (
        stream.text
        == b"""\
- -
    - "mmm"
    - y
  - - z
"""
    )


def test_same_line_triple_nested_change_type():
    stream = parse_str("""\
- - - x
    - y
  - - z
""")
    stream[0][0] = "mmm"
    assert (
        stream.text
        == b"""\
-
  - "mmm"
  - - z
"""
    )


def test_contains():
    stream = parse_str("""\
- abc
""")
    assert "abc" in stream
    assert "def" not in stream
