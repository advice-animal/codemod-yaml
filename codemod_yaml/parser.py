from __future__ import annotations

from dataclasses import dataclass
from logging import getLogger
from typing import Any, Dict, Optional, Union

from tree_sitter import Language, Parser, Tree
from tree_sitter_yaml import language as yaml_language

from .box.py import BoxedPy
from .box.yaml import boxyaml
from .box.yaml.mapping import YamlBlockMapping
from .box.yaml.sequence import YamlBlockSequence

logger = getLogger(__name__)
parser = Parser(Language(yaml_language()))

# These constants need to sort a certain way, and are applied from higher
# numbers downward.
CHANGE = 1
APPEND = 2
DELETE = 3


@dataclass(order=True)
class PendingEdit:
    start: int
    end: int
    action: int
    cookie: int
    item: Optional[BoxedPy] = None


class YamlStream:
    """
    The main object of loading and saving yaml files.

    For example, YamlStream.from_string(...).text is the simplest roundtrip.

    The document must already have some structure, e.g. the root should be a
    block map or sequence.  This is for making targeted edits to that.
    """

    _tree: Tree
    _root: Union[YamlBlockMapping, YamlBlockSequence]
    _original_bytes: bytes
    _edits: Dict[int, PendingEdit]

    def __init__(self, tree: Tree, original_bytes: bytes) -> None:
        self._tree = tree
        self._original_bytes = original_bytes
        self._edits = {}

        # TODO test more with streams that start with "---"
        doc = self._tree.root_node.children[0]

        # We forward getitem etc to this object
        node = boxyaml(node=doc.children[0], stream=self)
        assert isinstance(node, (YamlBlockMapping, YamlBlockSequence))
        self.root = node

    # Forwarding methods

    def __getitem__(self, key: Union[int, str]) -> Any:
        return self.root[key]  # type: ignore[index]

    @property
    def text(self) -> bytes:
        tmp = self._original_bytes

        # TODO verify edits are non-overlapping
        for edit in sorted(self._edits.values(), reverse=True):
            if edit.item:
                new_bytes = edit.item.to_bytes()
            else:
                new_bytes = b""
            logger.warning(
                "Apply edit: %r->%r @ %r",
                tmp[edit.start : edit.end],
                new_bytes,
                edit,
            )
            tmp = tmp[: edit.start] + new_bytes + tmp[edit.end :]
            # TODO restore tree-sitter edits if we can come up with the line/col values
            # self._tree.edit(edit.start, edit.end, edit.start + len(new_bytes), (0, 0), (0, 0))
        logger.warning("New text: %r", tmp)
        tmp = tmp.lstrip(b"\n")
        # TODO restore this as verification we made valid edits
        # assert parser.parse(tmp, old_tree=self._tree).root_node.text == tmp
        return tmp


def parse_str(data: str) -> YamlStream:
    original_bytes = data.encode("utf-8")
    return parse(original_bytes)


def parse(data: bytes) -> YamlStream:
    print(type(data))
    return YamlStream(tree=parser.parse(data), original_bytes=data)
