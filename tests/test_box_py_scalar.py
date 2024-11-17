import pytest

from codemod_yaml.box.py import boxpy
from codemod_yaml.box.py.scalar import PyScalarString, QuoteStyle

def test_smoke():
    temp = boxpy('foo')
    assert isinstance(temp, PyScalarString)
    assert temp.value == 'foo'
    assert temp.quote_style == QuoteStyle.AUTO
    assert temp.to_str() == '"foo"'

def test_all_quote_styles():
    temp = PyScalarString('foo', QuoteStyle.SINGLE)
    assert temp.to_str() == "'foo'"

    temp = PyScalarString('foo', QuoteStyle.DOUBLE)
    assert temp.to_str() == '"foo"'

    temp = PyScalarString('foo', QuoteStyle.BARE)
    assert temp.to_str() == 'foo'

def test_all_quote_styles_validation():
    temp = PyScalarString('\'', QuoteStyle.SINGLE)
    with pytest.raises(ValueError):
        temp.to_str()

    temp = PyScalarString("\"", QuoteStyle.DOUBLE)
    with pytest.raises(ValueError):
        temp.to_str()

    temp = PyScalarString('-1', QuoteStyle.BARE)
    with pytest.raises(ValueError):
        temp.to_str()

    # Someday this will work
    temp = PyScalarString('\'"', QuoteStyle.AUTO)
    with pytest.raises(ValueError):
        temp.to_str()
