from codemod_yaml import parse_str


def test_flow_ints():
    stream = parse_str("a: [1, 2, 3]\nb: [4, 5,   6]\n")
    assert list(stream["a"]) == [1, 2, 3]
    del stream["a"]
    # still verbatim
    assert stream.text == b"b: [4, 5,   6]\n"
    # now upgrade
    stream["b"].append(7)
    assert stream.text == b"b: [4, 5, 6, 7]\n"


def test_flow_strings():
    stream = parse_str("a: ['x', \"y\", z]\n")
    assert list(stream["a"]) == ["x", "y", "z"]
    del stream["a"][1]
    assert stream.text == b"a: ['x', z]\n"


def test_modify_inplace():
    stream = parse_str("a:\nb:\n [1, 2]\n")
    stream["b"][0] = "t"
    assert stream.text == b'a:\nb:\n ["t", 2]\n'
