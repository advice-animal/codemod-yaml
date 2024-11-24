import pytest

from codemod_yaml import parse_str
from codemod_yaml.items import item, Item, Float

def test_smoke():
    temp = item(1.2)
    assert isinstance(temp, Float)
    assert temp == 1.2
    assert 1.2 == temp
    assert temp.to_string() == '1.2'

def test_parse():
    assert parse_str("1.2")._root == 1.2
    assert parse_str("+.inf")._root == float("inf")
    assert parse_str("-.inf")._root == float("-inf")
    # nan returns false for most operations
    n = parse_str(".nan")._root
    assert str(n) == "nan"
    assert not (n < 0)
    assert not (n >= 0)
