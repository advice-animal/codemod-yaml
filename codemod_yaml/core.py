from __future__ import annotations

from dataclasses import dataclass, field
from itertools import count
from logging import getLogger, WARNING
from typing import Any, Dict, Optional, Union

from tree_sitter import Language, Node, Parser, Tree
from tree_sitter_yaml import language as yaml_language
from vmodule import VLOG_1

from .base import BaseYaml
from .convert import wrap

logger = getLogger(__name__)
parser = Parser(Language(yaml_language()))

COOKIE_GENERATOR = count()


@dataclass
class YamlStream:
    _tree: Tree
    root: Optional[BaseYaml] = None
    original_bytes: Optional[bytes] = b""
    _edits: Dict[int, Any] = field(default_factory=dict)

    def __post_init__(self):
        doc = self._tree.root_node.children[0]  # doesn't have to be the first if ---
        self.root = wrap(doc.children[0], self)

    @classmethod
    def from_string(cls, string) -> "YamlStream":
        original_bytes = string.encode("utf-8")
        return cls(_tree=parser.parse(original_bytes), original_bytes=original_bytes)

    def __getitem__(self, key: Union[int, str]) -> Any:
        return self.root[key]

    def __setitem__(self, key: Union[int, str], value: Any) -> None:
        self.root[key] = value

    def __delitem__(self, key: Union[int, str]) -> None:
        del self.root[key]

    def record_edit(self, in_place_of: BaseYaml, new_bytes: bytes) -> int:
        assert b"\n" not in new_bytes  # have to deal with line numbers for end_point
        new_end_point = (
            in_place_of.start_point[0],
            in_place_of.start_point[1]
            + len(new_bytes)
            - (in_place_of.end_byte - in_place_of.start_byte),
        )
        cookie = next(COOKIE_GENERATOR)
        # TODO if this is broader than an edit we currently have, remove the
        # narrower ones and invalidate their objects. I guess we have to keep
        # their objects around too, this is almost ready for a dataclass.
        self._edits[cookie] = (
            (  # sort key
                in_place_of.start_byte,
                cookie,
            ),
            (  # args
                in_place_of.start_byte,
                in_place_of.end_byte,
                in_place_of.start_byte + len(new_bytes),
                in_place_of.start_point,
                in_place_of.end_point,
                new_end_point,
            ),  # new bytes, for our own edit
            new_bytes,
        )
        return cookie

    @property
    def text(self) -> bytes:
        tmp = self.original_bytes

        # TODO verify edits are non-overlapping
        for edit in sorted(self._edits.values(), reverse=True):
            logger.log(
                WARNING,
                "Apply edit: %r->%r @ %r",
                tmp[edit[1][0] : edit[1][1]],
                edit[2],
                edit[1],
            )
            tmp = tmp[: edit[1][0]] + edit[2] + tmp[edit[1][1] :]
            self._tree.edit(*edit[1])
        logger.warning("New text: %r", tmp)
        tmp = tmp.lstrip(b"\n")
        assert parser.parse(tmp, old_tree=self._tree).root_node.text == tmp
        return tmp


def dump(node: Node, indent: str = "") -> None:
    print(indent, node.type, repr(node.text))
    for child in node.children:
        dump(child, indent + "  ")


if __name__ == "__main__":
    import pathlib
    import sys

    tree = parser.parse(pathlib.Path(sys.argv[1]).read_bytes())
    dump(tree.root_node)
    # start_byte, old_end_byte, new_end_byte, start_point, old_end_point, new_end_point
