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


def test_explicit_null_value_preserved():
    # A flow pair with an explicit null value like {a: ~} must not be confused
    # with a valueless pair like {a}.  When the mapping is annealed (e.g. by
    # adding a new key), to_string() was checking `self.value == None` which
    # is True for both cases, silently dropping the ": ~" for explicit nulls.
    stream = parse_str("{a: ~, b: 1}\n")
    stream["c"] = 2  # forces the whole flow mapping to anneal
    assert stream.text == b'{a: ~, b: 1, "c": 2}\n'


def test_valueless_flow_pair_preserved():
    # Valueless pairs like {a, b} (set-like) must still render without ": ~".
    stream = parse_str("{a, b}\n")
    stream["c"] = 2
    assert stream.text == b'{a, b, "c": 2}\n'
