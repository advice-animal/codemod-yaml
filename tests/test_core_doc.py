import pytest
from codemod_yaml.core import YamlStream

SIMPLE_YAML = """\
foo: bar
baz: luhrman
"""

DEMO_YAML = """\
foo:
 - 0
 - 1
 - 02
 - 0o3
 - 0x04
"""

DEMO_STRINGS = """\
- a
- "b"
- 'c'
- |
  d
"""


def test_parse_simple():
    doc = YamlStream.from_string(SIMPLE_YAML)
    first = doc["foo"]
    second = doc["foo"]
    assert first is second
    assert first == "bar"
    with pytest.raises(KeyError):
        doc["x"]
    with pytest.raises(KeyError):
        doc["x"]
    with pytest.raises(KeyError):
        doc[1]
    new_text = doc.text
    assert new_text == SIMPLE_YAML.encode("utf-8")

def test_parse_demo():
    doc = YamlStream.from_string(DEMO_YAML)
    first = doc["foo"]
    second = doc["foo"]
    assert first is second
    assert first[0] == 0
    assert first[1] == 1
    assert first[2] == 2
    assert first[3] == 3
    assert first[4] == 4
    with pytest.raises(IndexError):
        first[99]
    new_text = doc.text
    assert new_text == DEMO_YAML.encode("utf-8")

def test_parse_strings():
    doc = YamlStream.from_string(DEMO_STRINGS)
    assert doc[0] == "a"
    assert doc[1] == "b"
    assert doc[2] == "c"
    #assert doc[3] == "d"

def test_edit_int():
    doc = YamlStream.from_string(SIMPLE_YAML)
    doc["foo"] = 456
    new_text = doc.text
    assert new_text == b"foo: 456\nbaz: luhrman\n"

def test_edit_string():
    doc = YamlStream.from_string(SIMPLE_YAML)
    doc["foo"] = "abcdef"
    new_text = doc.text
    assert new_text == b"foo: abcdef\nbaz: luhrman\n"

def test_edit_del():
    doc = YamlStream.from_string(SIMPLE_YAML)
    del doc["foo"]
    new_text = doc.text
    assert new_text == b"baz: luhrman\n"
