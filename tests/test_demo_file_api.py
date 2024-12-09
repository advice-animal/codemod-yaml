from io import BytesIO
from pathlib import Path
from codemod_yaml import parse_file

DEMO = b"- foo\n"


def test_roundtrip(tmp_path) -> None:
    a = Path(tmp_path / "a.yml")
    a.write_bytes(DEMO)

    assert parse_file(a)[0] == "foo"
    assert parse_file(str(a))[0] == "foo"
    assert parse_file(BytesIO(DEMO))[0] == "foo"

    b = BytesIO()
    parse_file(BytesIO(DEMO)).save_file(b)
    assert b.getvalue() == DEMO

    c = Path(tmp_path / "c.yml")
    parse_file(BytesIO(DEMO)).save_file(c)
    assert c.read_bytes() == DEMO


def test_diff(capsys):
    doc = parse_file(BytesIO(DEMO))
    doc.append("bar")
    doc.show_diff()
    diff = capsys.readouterr().out
    assert (
        diff
        == """\
--- a/file.yml
+++ b/file.yml
@@ -1 +1,2 @@
 - foo
+- "bar"
"""
    )
