import ast

from ..base_types import UserInt, UserStr
from ..py.scalar import PyScalarString, QuoteStyle
from . import BoxedYaml, register

__all__ = [
    "YamlBareScalarString",
    "YamlSingleQuoteScalarString",
    "YamlDoubleQuoteScalarString",
    "YamlBlockScalarString",
    "YamlScalarInt",
]


class YamlBaseScalarString(BoxedYaml, UserStr):
    quote_style: QuoteStyle

    def upgrade(self) -> PyScalarString:
        return PyScalarString(self.value, self.quote_style)


@register("flow_node.plain_scalar.string_scalar")
class YamlBareScalarString(YamlBaseScalarString):
    quote_style = QuoteStyle.AUTO

    def __post_init__(self) -> None:
        node_bytes = self.node.text
        assert isinstance(node_bytes, bytes)
        self.value = node_bytes.decode("utf-8")


@register("flow_node.single_quote_scalar")
class YamlSingleQuoteScalarString(YamlBaseScalarString, UserStr):
    quote_style = QuoteStyle.SINGLE

    def __post_init__(self) -> None:
        node_bytes = self.node.text
        assert isinstance(node_bytes, bytes)
        self.value = ast.literal_eval(node_bytes.decode("utf-8"))


@register("flow_node.double_quote_scalar")
class YamlDoubleQuoteScalarString(YamlBaseScalarString, UserStr):
    quote_style = QuoteStyle.DOUBLE

    def __post_init__(self) -> None:
        node_bytes = self.node.text
        assert isinstance(node_bytes, bytes)
        self.value = ast.literal_eval(node_bytes.decode("utf-8"))


@register("flow_node.plain_scalar.integer_scalar")
class YamlScalarInt(BoxedYaml, UserInt):
    def __post_init__(self) -> None:
        node_bytes = self.node.text
        assert isinstance(node_bytes, bytes)
        self.string_value = node_bytes.decode("utf-8")
        t = self.string_value
        if t[0] == "0" and t[:2] not in ("0o", "0x") and t != "0":
            t = "0o" + t[1:]
        self.value = ast.literal_eval(t)


@register("block_node.block_scalar")
class YamlBlockScalarString(YamlBaseScalarString):
    def __post_init__(self) -> None:
        # TODO runs of spaces?
        node_bytes = self.node.text
        assert isinstance(node_bytes, bytes)
        self.value = node_bytes.decode("utf-8")[1:].strip().replace("\n", " ")

    def base_indent(self) -> str:
        return ""

    def to_str(self) -> str:
        # TODO handle wrapping
        return f"|-\n{self.base_indent()}{self.value}"
