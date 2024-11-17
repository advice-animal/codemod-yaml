from codemod_yaml import parse_str
from codemod_yaml import QuoteStyle, PyScalarString

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
    stream.append(PyScalarString("baz", QuoteStyle.BARE))
    assert stream.text == b"- foo\n- bar\n- baz\n"
    stream.append(PyScalarString("zab", QuoteStyle.BARE))
    assert stream.text == b"- foo\n- bar\n- baz\n- zab\n"

def test_edit_sequence2():
    stream = parse_str("- foo\n- bar\n- baz\n")
    del stream[1]
    assert stream.text == b"- foo\n- baz\n"
    stream.append(PyScalarString("zab", QuoteStyle.BARE))
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
    assert stream[3] == "d"
    # didn't make any edits, this should be fine
    assert stream.text == b"- a\n- \"b\"\n- 'c'\n- |\n  d\n"