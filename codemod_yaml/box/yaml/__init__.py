from __future__ import annotations

from typing import Callable, Optional, TYPE_CHECKING

from tree_sitter import Node

if TYPE_CHECKING:
    from ...parser import YamlStream


class BoxedYaml:
    """
    Boxed version of a yaml tree-sitter node.

    If you want to replace the whole node, talk to the parent; if you want to
    replace just a piece (for ones that are effectively "containers" then there
    should be methods here).
    """

    def __init__(self, node: Node, stream: "YamlStream"):
        self.node = node
        self.stream = stream
        self._cookie = None  # Not deleted... yet

        self.__post_init__()

    def __post_init__(self) -> None:
        pass

    def span(self) -> tuple[int, int]:
        # TODO feels like this should be +1 end
        return (self.node.start_byte, self.node.end_byte)


def boxyaml(node: Node, stream: "YamlStream") -> BoxedYaml:
    """
    Wraps a tree-sitter Node (of known type) to a BoxedYaml object.

    These are not used in edits except when deleted/replaced to find the span.
    """
    typ: Optional[type[BoxedYaml]]

    typ = REGISTRY_YAML.get(node.type)
    try:
        if typ is None:
            typ = REGISTRY_YAML.get(f"{node.type}.{node.children[0].type}")
            if typ is None:
                typ = REGISTRY_YAML.get(
                    f"{node.type}.{node.children[0].type}.{node.children[0].children[0].type}"
                )
    except IndexError:
        # If it doesn't have that many children, we give up early
        pass
    if typ is None:
        raise ValueError(f"Could not find wrapper for {node}")

    return typ(node=node, stream=stream)


REGISTRY_YAML: dict[str, type[BoxedYaml]] = {}


def register(yaml_path: str) -> Callable[[type[BoxedYaml]], type[BoxedYaml]]:
    def callable(cls: type[BoxedYaml]) -> type[BoxedYaml]:
        REGISTRY_YAML[yaml_path] = cls
        return cls

    return callable
