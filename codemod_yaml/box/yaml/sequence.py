from __future__ import annotations

from typing import Any, Union

from ..py import BoxedPy, boxpy
from ..py.sequence import PyBlockSequenceItem
from ..style import YamlStyle
from ..yaml import BoxedYaml, boxyaml, register

__all__ = ["YamlBlockSequence", "YamlBlockSequenceItem"]


@register("block_node.block_sequence")
class YamlBlockSequence(BoxedYaml):
    # block_sequence > block_sequence_item > flow_node > $value

    _count: int
    _items: dict[int, YamlBlockSequenceItem]

    def __post_init__(self) -> None:
        self._items = {}
        self._count = len(self.node.children[0].children)
        # It shouldn't be possible to parse a zero-length sequence, I hope.
        self._ensure(self._count - 1)
        self._yaml_style = self._items[self._count - 1].yaml_style

    def append(self, other: Any) -> None:
        if not isinstance(other, BoxedPy):
            other = boxpy(other)

        seq_item = PyBlockSequenceItem(other, yaml_style=self._yaml_style)

        self.stream.edit(self, seq_item, append=True)
        self._items[self._count] = other
        self._count += 1

    def __getitem__(self, index: int) -> Union[BoxedYaml, BoxedPy]:
        self._ensure(index)
        value = self._items[index].value  # note: lazy property
        assert isinstance(value, (BoxedYaml, BoxedPy))
        return value

    def __setitem__(self, index: int, other: Any) -> None:
        if not isinstance(other, BoxedPy):
            other = boxpy(other)

        t = self[index]
        if isinstance(t, BoxedYaml):
            self.stream.edit(t, other)
        self._items[index].value = other

    def __delitem__(self, index: int) -> None:
        self._ensure(index)
        if isinstance(self._items[index], BoxedYaml):
            self.stream.edit(self._items[index], None)
        # TODO fix count, etc

    def _ensure(self, index: int) -> None:
        if index not in self._items:
            node = boxyaml(self.node.children[0].children[index], stream=self.stream)
            assert isinstance(node, YamlBlockSequenceItem)
            self._items[index] = node


@register("block_sequence_item")
class YamlBlockSequenceItem(BoxedYaml):
    """
    Implementation detail.
    """

    _value: Union[BoxedYaml, BoxedPy, None] = None

    def get_value(self) -> Union[BoxedYaml, BoxedPy]:
        if not self._value:
            self._value = boxyaml(self.node.children[1], stream=self.stream)
        return self._value

    def set_value(self, other: BoxedPy) -> None:
        self._value = other

    value = property(get_value, set_value)

    @property
    def start_byte(self) -> int:
        expected_indent = self.node.start_point.column
        leading_whitespace = self.stream._original_bytes[
            self.node.start_byte - expected_indent : self.node.start_byte
        ]
        assert (
            leading_whitespace == b" " * expected_indent
        )  # can't handle same-line block like "- - a" yet
        return self.node.start_byte - expected_indent

    @property
    def end_byte(self) -> int:
        # TODO conditional
        return self.node.end_byte + 1

    @property
    def yaml_style(self) -> YamlStyle:
        expected_indent = self.node.start_point.column
        leading_whitespace = self.stream._original_bytes[
            self.node.start_byte - expected_indent : self.node.start_byte
        ]
        assert (
            leading_whitespace == b" " * expected_indent
        )  # can't handle same-line block like "- - a" yet
        after_dash = self.stream._original_bytes[
            self.node.children[0].end_byte : self.node.children[1].start_byte
        ]
        return YamlStyle(
            sequence_whitespace_before_dash=leading_whitespace.decode("utf-8"),
            sequence_whitespace_after_dash=after_dash.decode("utf-8"),
        )
