import pytest

from codemod_yaml.items import item, String, QuoteStyle


def test_smoke():
    temp = item("foo")
    assert isinstance(temp, String)
    assert temp == "foo"
    assert "foo" == temp
    assert temp.to_string() == '"foo"'


def test_all_quote_styles():
    temp = String("foo", QuoteStyle.SINGLE)
    assert temp.to_string() == "'foo'"

    temp = String("foo", QuoteStyle.DOUBLE)
    assert temp.to_string() == '"foo"'

    temp = String("foo", QuoteStyle.BARE)
    assert temp.to_string() == "foo"


def test_all_quote_styles_validation():
    temp = String("'", QuoteStyle.SINGLE)
    assert temp.to_string() == "'''"  # We trust the user :/
    temp = String("x", QuoteStyle.SINGLE_PREFERRED)
    assert temp.to_string() == "'x'"
    temp = String("'", QuoteStyle.SINGLE_PREFERRED)
    assert temp.to_string() == '"\'"'

    temp = String('"', QuoteStyle.DOUBLE)
    assert temp.to_string() == '"""'  # We trust the user :/
    temp = String("x", QuoteStyle.DOUBLE_PREFERRED)
    assert temp.to_string() == '"x"'
    temp = String("'", QuoteStyle.DOUBLE_PREFERRED)
    assert temp.to_string() == '"\'"'

    temp = String("-1", QuoteStyle.BARE)
    assert temp.to_string() == '-1'  # We trust the user :/
    temp = String("-1", QuoteStyle.BARE_PREFERRED)
    assert temp.to_string() == "'-1'"

    # Someday this will work
    temp = String("'\"", QuoteStyle.DOUBLE_PREFERRED)
    with pytest.raises(ValueError):
        temp.to_string()
