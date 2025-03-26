from codemod_yaml import parse_str


def test_simple_mapping():
    stream = parse_str("{x: y, z: 'foo'}\n")
    stream["x"] = "zzz"
    assert stream.text == b"{x: \"zzz\", z: 'foo'}\n"


def test_template_key():
    stream = parse_str("""\
replicas: {{ replicas }: null}
""")
    assert isinstance(stream["replicas"], dict)
    assert list(stream["replicas"].keys()) == ["{replicas}"]


def test_solo_template_key():
    stream = parse_str("""\
replicas: {{ replicas }}
""")
    assert isinstance(stream["replicas"], dict)
    assert list(stream["replicas"].keys()) == ["{replicas}"]
