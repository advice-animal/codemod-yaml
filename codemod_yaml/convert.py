from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tree_sitter import Node

    from .base import BaseSurrogate, BaseYaml
    from .core import YamlStream


def wrap(node: Node, stream: YamlStream) -> BaseYaml:
    typ = _dispatch.get(node.type)
    try:
        if typ is None:
            typ = _dispatch.get(f"{node.type}.{node.children[0].type}")
            if typ is None:
                typ = _dispatch.get(
                    f"{node.type}.{node.children[0].type}.{node.children[0].children[0].type}"
                )
    except IndexError:
        pass
    if typ is None:
        raise ValueError(f"Could not find wrapper for {node!r}: {node}")

    return typ(node, stream)


def wrap_native(obj: object, stream: YamlStream) -> BaseSurrogate:
    if isinstance(obj, int):
        return SurrogateIntegerScalar(stream, obj)
    elif isinstance(obj, str):
        # TODO somewhere need to decide if it gets quoted
        return SurrogateStringScalar(stream, obj)
    else:
        raise TypeError(type(obj))


from .mappings import YamlBlockMapping  # noqa: E402
from .scalars import (  # noqa: E402
    SurrogateIntegerScalar,
    SurrogateStringScalar,
    YamlIntegerScalar,
    YamlStringDoubleQuoteScalar,
    YamlStringScalar,
    YamlStringSingleQuoteScalar,
)
from .sequences import YamlBlockSequence  # noqa: E402

_dispatch = {
    "block_node.block_mapping": YamlBlockMapping,
    "block_node.block_sequence": YamlBlockSequence,
    # "flow_node.flow_sequence": YamlFlowSequence,
    # "flow_node.flow_mapping": YamlFlowMapping,
    "flow_node.plain_scalar.string_scalar": YamlStringScalar,
    "flow_node.plain_scalar.integer_scalar": YamlIntegerScalar,
    "flow_node.single_quote_scalar": YamlStringSingleQuoteScalar,
    "flow_node.double_quote_scalar": YamlStringDoubleQuoteScalar,
    # "block_node.block_scalar": YamlBlockScalar
}
