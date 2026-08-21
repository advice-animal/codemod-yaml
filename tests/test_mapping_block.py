import pytest
from codemod_yaml import parse_str, item


def test_simple_mapping():
    stream = parse_str("key: val\n")

    # Simple invariant, we should return the exact same object
    first = stream["key"]
    second = stream["key"]
    assert first is second

    assert stream["key"] == "val"
    # didn't make any edits, this should be fine
    assert stream.text == b"key: val\n"


def test_terribly_complex_document():
    stream = parse_str("""\
key1: !tag {a: 1, b: 2}
nulls:      { null, ~ }
key2:
 - seq1
 - |-
    some big item
    here
 - seq2
blah: [ 4, 5   , 6]
""")
    stream["key2"][2] = "new item"  # gets double quoted for now
    assert (
        stream.text.decode("utf-8")
        == """\
key1: !tag {a: 1, b: 2}
nulls:      { null, ~ }
key2:
 - seq1
 - |-
    some big item
    here
 - "new item"
blah: [ 4, 5   , 6]
"""
    )


def test_delete_nested_mapping():
    stream = parse_str("""\
key:
    a: b
    nested: value
    c: d
""")
    del stream["key"]["nested"]
    assert (
        stream.text
        == b"""key:
    a: b
    c: d
"""
    )


def test_anneal_mapping():
    stream = parse_str("""\
key:
    a: b
    nested: value
    c: d
""")
    stream["key"].anneal()
    assert (
        stream.text
        == b"""\
key:
    a: b
    nested: value
    c: d
"""
    )
    # TODO this isn't really confirming the code is executed, we rely on coverage
    stream["key"]["nested"] = {"a": "b"}
    stream["key"]["x"] = "y"
    assert (
        stream.text
        == b"""\
key:
    a: b
    "nested":
      "a": "b"
    c: d
    "x": "y"
"""
    )


def test_style_cascade():
    stream = parse_str("""\
key: value
""")
    x = item({"a": {"b": {"c": "d", "e": "f"}}})
    stream["key"] = x

    assert (
        stream.text
        == b"""\
key:
  "a":
    "b":
      "c": "d"
      "e": "f"
"""
    )


def test_key_types():
    stream = parse_str("""\
~: 1
1: 2
x:
""")
    assert stream[None] == 1
    assert stream[1] == 2
    assert stream["x"] == None


def test_comments_all_over_the_place():
    stream = parse_str("""\
# comment1
x: # comment2
    # comment3
    y
    # comment4
# comment5
z:
""")
    assert stream["x"] == "y"
    stream["x"] = "new"
    assert (
        stream.text
        == b"""\
# comment1
x: "new"
    # comment4
# comment5
z:
"""
    )


def test_sequence_keys():
    # Really, YAML?  I only let this work for one level of nesting.
    stream = parse_str("""\
[1, 2, 3]: foo
""")
    assert stream[(1, 2, 3)] == "foo"


def test_anchors():
    stream = parse_str("""\
a: b
c: &anchor
  d: foo
e: f
g: *anchor
""")
    assert stream["a"] == "b"
    assert stream["e"] == "f"

    with pytest.raises(NotImplementedError):
        stream["c"]
    with pytest.raises(NotImplementedError):
        stream["g"]

    stream["a"] = [2, 3]
    assert (
        stream.text
        == b"""\
a:
  - 2
  - 3
c: &anchor
  d: foo
e: f
g: *anchor
"""
    )


def test_other_dict_methods():
    stream = parse_str("""\
a: b
c: d
e: f
""")
    assert stream.pop("a") == "b"
    stream.setdefault("g", "h")
    assert (
        stream.text
        == b"""\
c: d
e: f
"g": "h"
"""
    )


def test_delitem_missing_key_no_state_corruption():
    import pytest
    stream = parse_str("a: 1\nb: 2\n")
    with pytest.raises(KeyError):
        del stream._root["missing"]
    # The mapping must NOT have been annealed as a side-effect of the failed delete.
    assert not stream._root._annealed
    # Subsequent targeted edits should still work (not fall back to full rewrite).
    stream["a"] = 99
    assert stream.text == b"a: 99\nb: 2\n"


def test_pop_missing_key_raises():
    import pytest
    stream = parse_str("a: 1\nb: 2\n")
    assert stream.pop("a") == 1
    # Mapping.pop without default must raise KeyError.
    with pytest.raises(KeyError):
        stream._root.pop("missing")
    # YamlStream.pop without default must also raise KeyError (not return None).
    with pytest.raises(KeyError):
        stream.pop("missing")
    # With an explicit default, missing key returns the default instead.
    assert stream._root.pop("missing", "fallback") == "fallback"
    assert stream.pop("missing", "fallback") == "fallback"


def test_unhashable_keys():
    stream = parse_str("""\
[1, 2,     3]: x
{4: 5}: y
""")
    assert list(stream._root.keys()) == [[1, 2, 3], "{4: 5}"]
    assert stream[[1, 2, 3]] == "x"
    assert stream["{4: 5}"] == "y"


def test_missing_values():
    stream = parse_str("""\
x:
y:
""")
    assert stream["x"] == None
    assert stream["y"] == None
    stream["x"] = "z"
    assert (
        stream.text
        == b"""\
x: "z"
y:
"""
    )

def test_setdefault_empty_dict():
    stream = parse_str("""\
x: y
""")
    stream.setdefault("z", {})
    # Empty block containers render inline; block style kicks in once items exist.
    assert stream.text == b'x: y\n"z": {}\n'
    stream["z"]["z"] = 1
    assert stream.text == b"""\
x: y
"z":
  "z": 1
"""


def test_implicit_null_survives_unrelated_edit():
    # An implicit null ("a:" with nothing after) used to be boxed as a plain
    # Null() with no original spelling, so a forced whole-mapping anneal (from
    # adding an unrelated key) rendered it as "a: ~" instead of leaving it empty.
    stream = parse_str("""\
a:
b: 1
""")
    stream["c"] = 2
    # Trailing space after "a:" comes from the pre-existing implicit-null
    # style default (one space), harmless and YAML-equivalent to "a:".
    assert stream.text == b'a: \nb: 1\n"c": 2\n'
    reparsed = parse_str(stream.text.decode("utf-8"))
    assert reparsed["a"] == None  # noqa: E711


def test_setdefault_chain():
    stream = parse_str("x: y\n")
    stream.setdefault("a", {})
    stream["a"].setdefault("b", {})
    stream["a"]["b"]["val"] = 1
    assert stream.text == b"""\
x: y
"a":
  "b":
    "val": 1
"""
