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
