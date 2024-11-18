from __future__ import annotations

from typing import Any, overload, Sequence, Union

from ..base_types import UserList
from ..py import BoxedPy, boxpy
from ..py.sequence import PyBlockSequenceItem
from ..style import YamlStyle
from ..yaml import BoxedYaml, boxyaml, register

__all__ = ["YamlBlockSequence", "YamlBlockSequenceItem"]


@register("block_node.block_sequence")
class YamlBlockSequence(BoxedYaml, UserList):
    # block_sequence > block_sequence_item > flow_node > $value

    _items: list[YamlBlockSequenceItem]  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self._items = [
            boxyaml(child, stream=self.stream)  # type: ignore[misc]
            for child in self.node.children[0].children
        ]
        # It shouldn't be possible to parse a zero-length sequence, I hope.
        self._yaml_style = self._items[-1].yaml_style

    def append(self, other: Any) -> None:
        if not isinstance(other, BoxedPy):
            other = boxpy(other)

        seq_item = PyBlockSequenceItem(other, yaml_style=self._yaml_style)

        other.cookie = self.stream.edit(self, seq_item, append=True)
        self._items.append(other)

    @overload
    def __getitem__(self, index: slice) -> list[Union[BoxedYaml, BoxedPy]]: ...
    @overload
    def __getitem__(self, index: int) -> Union[BoxedYaml, BoxedPy]: ...
    def __getitem__(self, index):  # type: ignore[no-untyped-def]
        if isinstance(index, slice):
            start, stop, step = index.indices(len(self._items))
            return [self[i] for i in range(start, stop, step)]
        value = self._items[index].value  # note: lazy property
        assert isinstance(value, (BoxedYaml, BoxedPy))
        return value

    @overload
    def __setitem__(self, index: slice, other: Sequence[Any]) -> None: ...
    @overload
    def __setitem__(self, index: int, other: Any) -> None: ...
    def __setitem__(self, index, other):  # type: ignore[no-untyped-def]
        if isinstance(index, slice):
            start, stop, step = index.indices(len(self._items))

            if step == 1 and stop == len(self._items):
                # Only handle the replace-end cases for now, since it's easy
                del self[index]
                for x in other:
                    self.append(x)
            else:
                assert len(other) == (stop - start) // step
                it = iter(other)
                for i in range(start, stop, step):
                    self[i] = next(it)
            return

        if not isinstance(other, BoxedPy):
            other = boxpy(other)

        t = self[index]
        if isinstance(t, BoxedYaml):
            other.cookie = self.stream.edit(t, other)
        self._items[index].value = other

    @overload
    def __delitem__(self, index: slice) -> None: ...
    @overload
    def __delitem__(self, index: int) -> None: ...
    def __delitem__(self, index):  # type: ignore[no-untyped-def]
        if isinstance(index, slice):
            start, stop, step = index.indices(len(self._items))
            for i in range(start, stop, step):
                if isinstance(self._items[i], BoxedYaml):
                    self.stream.edit(self._items[i], None)
            del self._items[index]
            return
        if isinstance(self._items[index], BoxedYaml):
            self.stream.edit(self._items[index], None)
        elif isinstance(self._items[index], BoxedPy):
            self.stream.cancel_cookie(self._items[index].cookie)
        del self._items[index]

    def _ensure(self, index: int) -> None:
        if index not in self._items:
            node = boxyaml(self.node.children[0].children[index], stream=self.stream)
            assert isinstance(node, YamlBlockSequenceItem)
            self._items[index] = node

    @property
    def end_byte(self) -> int:
        text = self.node.text
        assert isinstance(text, bytes)
        if text[-1:] == b"\n":
            return self.node.end_byte
        else:
            return self.node.end_byte + 1


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
            self.stream._original_bytes[
                self.node.start_byte
                - expected_indent
                - 1 : self.node.start_byte
                - expected_indent
            ]
            == b"\n"
        )
        assert (
            leading_whitespace == b" " * expected_indent
        )  # can't handle same-line block like "- - a" yet
        return self.node.start_byte - expected_indent

    @property
    def end_byte(self) -> int:
        text = self.node.text
        assert isinstance(text, bytes)
        if text[-1:] == b"\n":
            return self.node.end_byte
        else:
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

    def __eq__(self, other: object) -> bool:
        return self.value == other  # type: ignore[no-any-return]
