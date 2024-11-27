import pytest
from pathlib import Path
from codemod_yaml import parse_str, ParseError

INVALID_PATH = Path(__file__).parent / "invalid.yaml"
INVALID_TEXT = INVALID_PATH.read_text()


def test_parse_error():
    with pytest.raises(ParseError):
        parse_str(INVALID_TEXT)
