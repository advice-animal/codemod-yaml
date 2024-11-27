from pathlib import Path
from codemod_yaml.cyq import main


def test_good(capsys):
    rv = main(["options.test-versions", str(Path(__file__).parent / "complex.yaml")])
    assert rv == 0
    lines = capsys.readouterr().out.splitlines(True)
    assert lines[0].endswith("complex.yaml\n"), lines[0]
    assert lines[1] == "   options.test-versions = ['3.8', '3.9']\n"


def test_sequence_indexing(capsys):
    rv = main(["options.test-versions.0", str(Path(__file__).parent / "complex.yaml")])
    assert rv == 0
    lines = capsys.readouterr().out.splitlines(True)
    assert lines[0].endswith("complex.yaml\n"), lines[0]
    assert lines[1] == "   options.test-versions.0 = '3.8'\n"


def test_bad(capsys):
    rv = main(
        [
            "options.test-versions",
            str(Path(__file__).parent / "complex.yaml.doesnotexist"),
        ]
    )
    assert rv == 1
    lines = capsys.readouterr().out.splitlines(True)
    assert lines[0].endswith("complex.yaml.doesnotexist\n"), lines[0]
    assert "  options.test-versions = FileNotFoundError" in lines[1], lines[1]
