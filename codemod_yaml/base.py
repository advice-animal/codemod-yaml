from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tree_sitter import Node

    from .core import YamlStream


@dataclass
class BaseYaml:
    """
    A wrapper for tree-sitter yaml Nodes.

    Subclasses that implement this should be registered in
    `codemod_yaml/convert.py` and wrap their children lazily.
    """

    node: Node
    stream: "YamlStream"


@dataclass
class BaseSurrogate:
    stream: YamlStream

    def to_bytes(self) -> bytes:
        raise NotImplementedError


class _Erasure:
    pass


ERASURE = _Erasure()
