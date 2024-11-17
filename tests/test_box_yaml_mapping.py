from codemod_yaml import parse_str

def test_simple_mapping():
    stream = parse_str("key: val\n")
    
    # Simple invariant, we should return the exact same object
    first = stream["key"]
    second = stream["key"]
    assert first is second

    assert stream["key"] == "val"
    # didn't make any edits, this should be fine
    assert stream.text == b"key: val\n"

def test_terribly_complex_document():
    stream = parse_str("""\
key1: !tag {a: 1, b: 2}
nulls:      { null, ~ }
key2:
 - seq1
 - |-
    some big item
    here
 - seq2
blah: [ 4, 5   , 6]
""")
    stream["key2"][2] = "new item" # gets double quoted for now
    assert stream.text.decode("utf-8") == """\
key1: !tag {a: 1, b: 2}
nulls:      { null, ~ }
key2:
 - seq1
 - |-
    some big item
    here
 - "new item"
blah: [ 4, 5   , 6]
"""

def test_delete_nested_mapping():
    stream = parse_str("""\
key:
    a: b
    nested: value
    c: d
""")
    del stream["key"]["nested"]
    assert stream.text == b"""key:
    a: b
    c: d
"""
