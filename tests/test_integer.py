from codemod_yaml import parse_str
from codemod_yaml.items import item, Integer


def test_smoke():
    temp = item(1000)
    assert isinstance(temp, Integer)
    assert temp == 1000
    assert 1000 == temp
    assert temp.to_string() == "1000"


def test_parse():
    assert parse_str("1000")._root == 1000
    assert parse_str("0o11")._root == 9
    assert parse_str("0x11")._root == 17
