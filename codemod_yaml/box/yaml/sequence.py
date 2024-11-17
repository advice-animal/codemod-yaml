from __future__ import annotations

from typing import Union

from ..py import BoxedPy

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

    def __getitem__(self, index: int) -> Union[BoxedYaml, BoxedPy]:
        if index in self._items:
            value = self._items[index].value  # note: lazy property
            assert isinstance(value, (BoxedYaml, BoxedPy))
            return value

        node = boxyaml(self.node.children[0].children[index], stream=self.stream)
        assert isinstance(node, YamlBlockSequenceItem)
        self._items[index] = node
        value = node.value
        assert isinstance(value, BoxedYaml)
        return value


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
