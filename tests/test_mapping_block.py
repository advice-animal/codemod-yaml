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
