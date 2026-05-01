from codemod_yaml import parse_str
from codemod_yaml.items import item, Float


def test_smoke():
    temp = item(1.2)
    assert isinstance(temp, Float)
    assert temp == 1.2
    assert 1.2 == temp
    assert temp.to_string() == "1.2"


def test_parse():
    assert parse_str("1.2")._root == 1.2
    assert parse_str("1.5e20")._root == 1.5e20
    assert parse_str("+.inf")._root == float("inf")
    assert parse_str("-.inf")._root == float("-inf")
    # nan returns false for most operations
    n = parse_str(".nan")._root
    assert str(n) == "nan"
    assert n != n


def test_scientific():
    assert item(1.5e20).to_string() == "1.5e+20"


def test_special_cases():
    assert item(float("nan")).to_string() == ".nan"
    assert item(float("inf")).to_string() == ".inf"
    assert item(float("-inf")).to_string() == "-.inf"


def test_mixed_case_inf_nan():
    # tree-sitter-yaml (following YAML 1.1) accepts .Inf, .INF, .NaN, .NAN.
    # Float.from_yaml used a case-sensitive endswith check so these variants
    # were not stripped of the dot before calling float(), raising ValueError.
    import math
    for s in [".Inf", ".INF", "+.INF", "-.INF", ".NaN", ".NAN"]:
        root = parse_str(s)._root
        if "nan" in s.lower():
            assert math.isnan(root)
        elif "-" in s:
            assert root == float("-inf")
        else:
            assert root == float("inf")
