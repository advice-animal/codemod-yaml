import pytest

from yaml import load, dump, Loader

from codemod_yaml.items import item, String, QuoteStyle
from codemod_yaml.parser import parser
from codemod_yaml.string_repr import safe_plain_repr, safe_dq_repr, safe_sq_repr


def test_smoke():
    temp = item("foo")
    assert isinstance(temp, String)
    assert temp == "foo"
    assert "foo" == temp
    assert temp.to_string() == '"foo"'


def test_all_explicit_quote_styles():
    temp = String("foo", QuoteStyle.SINGLE)
    assert temp.to_string() == "'foo'"

    temp = String("foo", QuoteStyle.DOUBLE)
    assert temp.to_string() == '"foo"'

    temp = String("foo", QuoteStyle.PLAIN)
    assert temp.to_string() == "foo"


def test_all_quote_styles_validation():
    temp = String("'", QuoteStyle.SINGLE)
    assert temp.to_string() == "''''"
    temp = String("x", QuoteStyle.SINGLE_PREFERRED)
    assert temp.to_string() == "'x'"
    temp = String("'", QuoteStyle.SINGLE_PREFERRED)
    assert temp.to_string() == "''''"

    temp = String('"', QuoteStyle.DOUBLE)
    assert temp.to_string() == '"\\""'  # We trust the user :/
    temp = String("x", QuoteStyle.DOUBLE_PREFERRED)
    assert temp.to_string() == '"x"'
    temp = String("'", QuoteStyle.DOUBLE_PREFERRED)
    assert temp.to_string() == '"\'"'

    temp = String("-1", QuoteStyle.PLAIN)
    assert temp.to_string() == '"-1"'
    temp = String("-1", QuoteStyle.PLAIN_PREFERRED)
    assert temp.to_string() == "'-1'"

    temp = String("'\"", QuoteStyle.DOUBLE_PREFERRED)
    assert temp.to_string() == '"\'\\""'
    temp = String("'\"", QuoteStyle.DOUBLE)
    assert temp.to_string() == '"\'\\""'


SAMPLE_STRINGS = [chr(i) for i in range(256)]


@pytest.mark.parametrize("c", SAMPLE_STRINGS)
def test_plain_escaping(c):
    t = safe_plain_repr(c)
    # dump appears to output 3 distinct styles:
    # 1. things that can be represented plain are, with a newline after
    # 2. but some have "\n..." (as in three dots) after
    # 3. ones that are complex enough are quoted
    if t is None:
        u = dump(c).strip()
        assert u[:1] in "\"'"
    elif c == "=":
        # we can't load this with pyyaml, there's a bug
        # https://github.com/yaml/pyyaml/issues/846
        assert t == c
    else:
        assert load(t, Loader=Loader) == c


@pytest.mark.parametrize("c", SAMPLE_STRINGS)
def test_plain_parsing(c):
    # This presumes the escaping is valid, tested above
    t = safe_plain_repr(c)
    if t is not None:
        y = parser.parse(t.encode("utf-8"))
        flow_node = y.root_node.children[0].children[0]
        assert item(flow_node, stream=object()) == c


@pytest.mark.parametrize("c", SAMPLE_STRINGS)
def test_sq_escaping(c):
    t = safe_sq_repr(c)
    if c == "\n":
        # this is subject to string folding when reading with pyyaml
        assert t is None
    elif t is None:
        u = dump(c).strip()
        assert u[:1] != "'"
    else:
        assert load(t, Loader=Loader) == c


@pytest.mark.parametrize("c", SAMPLE_STRINGS)
def test_sq_parsing(c):
    # This presumes the escaping is valid, tested above
    t = safe_sq_repr(c)
    if t is not None:
        y = parser.parse(t.encode("utf-8"))
        flow_node = y.root_node.children[0].children[0]
        assert item(flow_node, stream=object()) == c


@pytest.mark.parametrize("c", SAMPLE_STRINGS)
def test_dq_escaping(c):
    t = safe_dq_repr(c)
    print(repr(c), "->", t)
    assert load(t, Loader=Loader) == c


@pytest.mark.parametrize("c", SAMPLE_STRINGS)
def test_dq_parsing(c):
    # This presumes the escaping is valid, tested above
    t = safe_dq_repr(c)
    if t is not None:
        y = parser.parse(t.encode("utf-8"))
        flow_node = y.root_node.children[0].children[0]
        assert item(flow_node, stream=object()) == c


def test_safe_plain_repr_float_keywords():
    # YAML float keywords must never be emitted as plain scalars; they round-trip
    # as float infinity or NaN, not as strings.
    for kw in [".inf", ".Inf", ".INF", "+.inf", "+.Inf", "+.INF",
               "-.inf", "-.Inf", "-.INF", ".nan", ".NaN", ".NAN"]:
        assert safe_plain_repr(kw) is None, f"{kw!r} should be rejected"


def test_safe_plain_repr_float_exponent_sign():
    # Scientific notation with an explicit sign must be rejected; YAML parses
    # them as floats and they would round-trip as numbers, not strings.
    assert safe_plain_repr("1e+5") is None
    assert safe_plain_repr("1e-3") is None
    assert safe_plain_repr("2.5e+10") is None
    assert safe_plain_repr("9E-1") is None
    # Unsigned exponents were already caught
    assert safe_plain_repr("1e5") is None


def test_safe_plain_repr_binary_literals():
    # Multi-digit binary literals must be rejected; they round-trip as integers.
    assert safe_plain_repr("0b0") is None
    assert safe_plain_repr("0b1") is None
    assert safe_plain_repr("0b10") is None
    assert safe_plain_repr("0b101") is None
    assert safe_plain_repr("0b11111111") is None
    # Same for multi-digit octal
    assert safe_plain_repr("0o10") is None
    assert safe_plain_repr("0o777") is None
    # Plain identifiers that start with 0b/0o but aren't literals are fine
    assert safe_plain_repr("0b2") is not None  # not a valid binary literal
    assert safe_plain_repr("0b") is not None   # no digits


def test_safe_plain_repr():
    # assert safe_plain_repr("null null") == "null null"
    assert safe_plain_repr("null: null") is None
    assert safe_plain_repr("null") is None
    assert safe_plain_repr(",") is None

    for i in range(256):
        c = chr(i)
        if c in ("\n", "\x1b", "\x85", "\xa0"):
            continue
        # if i in (20, 33, 34, 39, 45, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 62, 63, 64, 124, 126):
        #    # these can't be escaped, it seems
        yaml_text = dump(c).encode("utf-8")
        y = parser.parse(yaml_text)
        # else:
        #     y = parser.parse(c.encode("utf-8"))
        print(i, repr(c), yaml_text)

        try:
            flow_node = y.root_node.children[0].children[0]
            assert item(flow_node, stream=object()) == c
        except IndexError:
            assert safe_plain_repr(c) is None
