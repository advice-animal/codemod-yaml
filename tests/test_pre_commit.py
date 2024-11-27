from codemod_yaml import parse_str
import moreorless

# The canonical pre-commit config includes sequence+map on same line
SAMPLE = """\
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.1
    hooks:
      - id: ruff
        args: [ --fix ]
      - id: ruff-format
"""


def test_pre_commit():
    doc = parse_str(SAMPLE)
    assert doc["repos"][0]["repo"] == "https://github.com/astral-sh/ruff-pre-commit"
    assert doc["repos"][0]["rev"] == "v0.6.1"
    assert doc["repos"][0]["hooks"][0]["id"] == "ruff"
    assert doc["repos"][0]["hooks"][0]["args"] == ["--fix"]


def test_modification():
    doc = parse_str(SAMPLE)
    doc["repos"][0]["repo"] = "foo"
    output = moreorless.unified_diff(
        SAMPLE, doc.text.decode("utf-8"), filename=".pre-commit-config.yaml", n=0
    )
    assert (
        output
        == """\
--- a/.pre-commit-config.yaml
+++ b/.pre-commit-config.yaml
@@ -2 +2,2 @@
-  - repo: https://github.com/astral-sh/ruff-pre-commit
+  -
+    repo: "foo"
"""
    )
