"""
This demonstrates that all the pieces of `complex.yaml` can be edited in a straightforward way.  Expected values are unified diffs with 0 lines context to make it more obvious that other lines are not being touched.
"""

from pathlib import Path
from codemod_yaml import parse_str, String, QuoteStyle
import moreorless

COMPLEX_PATH = Path(__file__).parent / "complex.yaml"
COMPLEX_TEXT = COMPLEX_PATH.read_text()


def test_style_automatic_string():
    stream = parse_str(COMPLEX_TEXT)
    assert stream["style"] == "setuptools"
    stream["style"] = "hatch"
    output = moreorless.unified_diff(
        COMPLEX_TEXT, stream.text.decode("utf-8"), filename="complex.yaml", n=0
    )

    assert (
        output
        == """\
--- a/complex.yaml
+++ b/complex.yaml
@@ -1 +1 @@
-style: setuptools
+style: "hatch"
"""
    )


def test_style_bare_string():
    stream = parse_str(COMPLEX_TEXT)
    stream["style"] = String("hatch", QuoteStyle.BARE)
    output = moreorless.unified_diff(
        COMPLEX_TEXT, stream.text.decode("utf-8"), filename="complex.yaml", n=0
    )

    assert (
        output
        == """\
--- a/complex.yaml
+++ b/complex.yaml
@@ -1 +1 @@
-style: setuptools
+style: hatch
"""
    )


def test_tool_version_python():
    stream = parse_str(COMPLEX_TEXT)
    stream["options"]["tool-versions"]["python"] = "3.13"
    output = moreorless.unified_diff(
        COMPLEX_TEXT, stream.text.decode("utf-8"), filename="complex.yaml", n=0
    )

    assert (
        output
        == """\
--- a/complex.yaml
+++ b/complex.yaml
@@ -7 +7 @@
-    python: "3.10"
+    python: "3.13"
"""
    )


def test_tool_version_java():
    stream = parse_str(COMPLEX_TEXT)
    stream["options"]["tool-versions"]["java"] = "17"
    output = moreorless.unified_diff(
        COMPLEX_TEXT, stream.text.decode("utf-8"), filename="complex.yaml", n=0
    )

    assert (
        output
        == """\
--- a/complex.yaml
+++ b/complex.yaml
@@ -9 +9 @@
-      "11"
+      "17"
"""
    )


def test_tool_version_delete_java():
    stream = parse_str(COMPLEX_TEXT)
    del stream["options"]["tool-versions"]["java"]
    output = moreorless.unified_diff(
        COMPLEX_TEXT, stream.text.decode("utf-8"), filename="complex.yaml", n=0
    )

    assert (
        output
        == """\
--- a/complex.yaml
+++ b/complex.yaml
@@ -8,2 +7,0 @@
-    java:
-      "11"
"""
    )


def test_tool_version_modify_flow_list_nodejs():
    stream = parse_str(COMPLEX_TEXT)
    stream["options"]["tool-versions"]["nodejs"] = ["99"]
    output = moreorless.unified_diff(
        COMPLEX_TEXT, stream.text.decode("utf-8"), filename="complex.yaml", n=0
    )

    assert (
        output
        == """\
--- a/complex.yaml
+++ b/complex.yaml
@@ -10 +10,2 @@
-    nodejs: ["14", "16"]  # comment
+    nodejs:
+      - "99"
"""
    )


def test_tool_version_delete_nodejs():
    stream = parse_str(COMPLEX_TEXT)
    del stream["options"]["tool-versions"]["nodejs"]
    output = moreorless.unified_diff(
        COMPLEX_TEXT, stream.text.decode("utf-8"), filename="complex.yaml", n=0
    )

    assert (
        output
        == """\
--- a/complex.yaml
+++ b/complex.yaml
@@ -10 +9,0 @@
-    nodejs: ["14", "16"]  # comment
"""
    )


def test_test_version_python():
    assert COMPLEX_TEXT.endswith("\n")  # Editing last item gets mangled otherwise
    stream = parse_str(COMPLEX_TEXT)
    assert stream["options"]["test-versions"] == ["3.8", "3.9"]
    assert stream["options"]["test-versions"] != ["3.8"]  # compare the whole thing
    assert stream["options"]["test-versions"] != ["3.9", "3.8"]  # order matters
    stream["options"]["test-versions"][1:] = ["3.12", "3.13"]
    output = moreorless.unified_diff(
        COMPLEX_TEXT, stream.text.decode("utf-8"), filename="complex.yaml", n=0
    )

    assert (
        output
        == """\
--- a/complex.yaml
+++ b/complex.yaml
@@ -14 +14,2 @@
-    - "3.9"
+    - "3.12"
+    - "3.13"
"""
    )
