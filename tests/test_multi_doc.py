"""
A single yaml file with multiple documents.
"""

from pathlib import Path
from codemod_yaml import parse_str
import moreorless

MULTI_DOC_PATH = Path(__file__).parent / "multi_doc.yaml"
MULTI_DOC_TEXT = MULTI_DOC_PATH.read_text()


def test_value_replacement_doc_0():
    stream = parse_str(MULTI_DOC_TEXT)
    assert stream.documents[0]["kind"] == "Deployment"
    stream.documents[0]["kind"] = "CronJob"
    output = moreorless.unified_diff(
        MULTI_DOC_TEXT, stream.text.decode("utf-8"), filename="multi_doc.yaml", n=0
    )

    assert (
        output
        == """\
--- a/multi_doc.yaml
+++ b/multi_doc.yaml
@@ -2 +2 @@
-kind: Deployment
+kind: "CronJob"
"""
    )


def test_value_replacement_doc_1():
    stream = parse_str(MULTI_DOC_TEXT)
    assert stream.documents[1]["metadata"]["name"] == "nginx-state-gatherer"
    stream.documents[1]["metadata"]["name"] = "apache-state-gatherer"
    output = moreorless.unified_diff(
        MULTI_DOC_TEXT, stream.text.decode("utf-8"), filename="multi_doc.yaml", n=0
    )

    assert (
        output
        == """\
--- a/multi_doc.yaml
+++ b/multi_doc.yaml
@@ -11 +11 @@
-  name: nginx-state-gatherer
+  name: "apache-state-gatherer"
"""
    )
