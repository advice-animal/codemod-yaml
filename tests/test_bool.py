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
