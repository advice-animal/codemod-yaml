from codemod_yaml import parse_str
from codemod_yaml.items import item, Boolean


def test_smoke():
    temp = item(True)
    assert isinstance(temp, Boolean)
    assert temp == True
    assert temp == 1
    assert temp != 2
    assert 1 == temp
    assert True == temp
    assert temp.to_string() == "true"
    assert item(True) == item(True)
    assert item(True) != item(False)


def test_parse():
    assert parse_str("true")._root == True
    assert parse_str("false")._root == False


def test_original_spelling_survives_unrelated_edit():
    # Adding a new key forces the whole mapping to re-render, which used to
    # normalize every sibling bool value to lowercase regardless of how it was
    # originally spelled.
    stream = parse_str(
        """\
a: true
b: True
c: TRUE
d: false
e: False
"""
    )
    stream["f"] = 1
    assert (
        stream.text
        == b"""\
a: true
b: True
c: TRUE
d: false
e: False
"f": 1
"""
    )


def test_original_spelling_survives_sequence_append():
    stream = parse_str(
        """\
- true
- True
- FALSE
"""
    )
    stream.append(1)
    assert (
        stream.text
        == b"""\
- true
- True
- FALSE
- 1
"""
    )
