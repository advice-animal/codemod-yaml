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
    with pytest.raises(ValueError):
        temp.to_string()
    temp = String("'", QuoteStyle.SINGLE_PREFERRED)
    assert temp.to_string() == '"\'"'

    temp = String('"', QuoteStyle.DOUBLE)
    with pytest.raises(ValueError):
        temp.to_string()
    temp = String("'", QuoteStyle.DOUBLE_PREFERRED)
    assert temp.to_string() == '"\'"'

    temp = String("-1", QuoteStyle.BARE)
    with pytest.raises(ValueError):
        temp.to_string()

    # Someday this will work
    temp = String("'\"", QuoteStyle.DOUBLE_PREFERRED)
    with pytest.raises(ValueError):
        temp.to_string()
