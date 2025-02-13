from pathlib import Path
from codemod_yaml import parse_str
import moreorless

SCALAR_PATH = Path(__file__).parent / "scalar.yaml"
SCALAR_TEXT = SCALAR_PATH.read_text()


def test_weird_keys_retained():
    stream = parse_str(SCALAR_TEXT)
    stream["z"] = "z"
    output = moreorless.unified_diff(
        SCALAR_TEXT, stream.text.decode("utf-8"), filename="complex.yaml", n=0
    )

    assert (
        output
        == """\
--- a/complex.yaml
+++ b/complex.yaml
+"z": "z"
"""
    )
