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


def test_sq_multiline_folding():
    # Single-quoted YAML scalars that span multiple lines must have YAML
    # flow-scalar line-folding applied: a single line break folds to a space;
    # N consecutive line breaks fold to N-1 newlines.
    from codemod_yaml import parse_str
    from codemod_yaml.string_repr import unescape_sq

    # pyyaml serialises '\n' as "- '\n\n  '\n" (two newlines → one after folding)
    assert parse_str("- '\n\n  '\n")[0] == '\n'
    # pyyaml serialises 'a\nb' as "- 'a\n\n  b'\n"
    assert parse_str("- 'a\n\n  b'\n")[0] == 'a\nb'
    # Single line-break folds to a space
    assert unescape_sq("'hello\n  world'") == 'hello world'
    # Trailing whitespace before the break is also stripped
    assert unescape_sq("'a  \n  b'") == 'a b'
    # Quote-doubling still works after folding
    assert unescape_sq("'it''''s'") == "it''s"


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


def test_unescape_yaml12_escape_sequences():
    # YAML 1.2 defines escape sequences not in the original PRETTY_ESCAPES dict.
    # _unescape fell through to chr(int(...)) for unknown escapes, crashing on
    # non-octal characters like \/ and \e.
    from codemod_yaml.string_repr import unescape_dq
    assert unescape_dq(r'"\/"') == "/"
    assert unescape_dq(r'"\e"') == "\x1b"
    assert unescape_dq(r'"\ "') == " "
    assert unescape_dq(r'"\N"') == "\x85"
    assert unescape_dq(r'"\L"') == " "
    assert unescape_dq(r'"\P"') == " "


def test_unescape_8digit_unicode():
    # YAML 1.2 defines \Uxxxxxxxx for code points above U+FFFF.  ESCAPE_RE was
    # matching \U as the catch-all \\[^ux] alternative (2 chars), causing
    # _unescape to call chr(int("U...")) which raised ValueError.
    from codemod_yaml.string_repr import unescape_dq
    assert unescape_dq(r'"\U0001F600"') == "\U0001F600"  # emoji
    assert unescape_dq(r'"\U00000041"') == "A"


def test_safe_plain_repr_empty_string():
    # An empty plain scalar is parsed as null in YAML 1.2; the empty string
    # must never be emitted as a plain scalar.
    assert safe_plain_repr("") is None


def test_safe_plain_repr_space_hash():
    # A space followed by '#' inside a plain scalar is a comment indicator in
    # YAML: everything from the '#' to end-of-line is stripped.  The scalar
    # must be quoted so the '#' is not consumed as a comment.
    assert safe_plain_repr("foo #bar") is None
    assert safe_plain_repr("x #") is None
    assert safe_plain_repr("value # comment") is None
    # Hash without preceding space is fine in plain scalars.
    assert safe_plain_repr("foo#bar") == "foo#bar"
    assert safe_plain_repr("#leading") is None  # already caught by ^\#


def test_safe_plain_repr_colon_at_end():
    # A trailing colon is parsed as a mapping-value indicator by YAML; both
    # pyyaml and tree-sitter raise errors when 'key: foo:\n' is parsed.
    assert safe_plain_repr("foo:") is None
    assert safe_plain_repr("key:") is None
    # Colon in the middle (not followed by space/end) is fine.
    assert safe_plain_repr("foo:bar") == "foo:bar"
    assert safe_plain_repr("http://example.com") == "http://example.com"


def test_safe_plain_repr_case_insensitive_keywords():
    # tree-sitter-yaml (following YAML 1.1) recognises case variants of null
    # and bool keywords.  Plain scalars matching these must be rejected so they
    # don't round-trip as None/True/False instead of as strings.
    for kw in ["NULL", "Null"]:
        assert safe_plain_repr(kw) is None, f"{kw!r} should be rejected (null)"
    for kw in ["True", "False", "TRUE", "FALSE"]:
        assert safe_plain_repr(kw) is None, f"{kw!r} should be rejected (bool)"
    # Lower-case forms were already caught; check they still are.
    assert safe_plain_repr("null") is None
    assert safe_plain_repr("true") is None
    assert safe_plain_repr("false") is None


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


def test_safe_plain_repr_leading_dot_floats():
    # Floats with a leading decimal point are valid YAML and must be rejected.
    assert safe_plain_repr(".5") is None
    assert safe_plain_repr("-.5") is None
    assert safe_plain_repr("+.5") is None
    # Floats with a trailing decimal point (no fractional digits) must also be rejected.
    assert safe_plain_repr("1.") is None
    # Positive-signed floats must be rejected.
    assert safe_plain_repr("+1.5") is None
    assert safe_plain_repr("+1e5") is None


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
