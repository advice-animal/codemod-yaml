from __future__ import annotations

import abc

from typing import Any, Optional

from tree_sitter import Node, Tree


class YamlStream(abc.ABC):
    _root: Item

    def __init__(self, tree: Tree, original_bytes: bytes):
        self._tree = tree
        self._original_bytes = original_bytes

    @abc.abstractmethod
    def cancel_cookie(self, cookie: int) -> None:
        pass

    @abc.abstractmethod
    def edit(self, item: Item, new_item: Optional[Item]) -> int:
        pass

    # Forwarding methods

    def __contains__(self, value: Any) -> bool:
        assert isinstance(self._root, (list, dict))
        return value in self._root

    def __getitem__(self, key: Any) -> Any:
        assert isinstance(self._root, (list, dict))
        return self._root[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        assert isinstance(self._root, (list, dict))
        self._root[key] = value

    def __delitem__(self, key: Any) -> None:
        assert isinstance(self._root, (list, dict))
        del self._root[key]

    def append(self, other: Any) -> None:
        assert isinstance(self._root, list)
        self._root.append(other)

    def get(self, other: Any, default: Any = None) -> Any:
        assert isinstance(self._root, dict)
        return self._root.get(other, default)

    def pop(self, other: Any, default: Any = None) -> Any:
        if isinstance(self._root, list):
            return self._root.pop(other)

        assert isinstance(self._root, dict)
        return self._root.pop(other, default)

    def setdefault(self, other: Any, value: Any) -> Any:
        assert isinstance(self._root, dict)
        return self._root.setdefault(other, value)


class Item(abc.ABC):
    """
    An `Item` is a dual-nature box -- it can wrap a `tree_sitter.Node` or just a python object.

    The specialized subclass should inherit from the python base type, which is why there isn't a
    `value` or so in the `__init__` here.  See `Integer` for a good example of this.  Scalars like
    keys are eagerly boxed for simplicity, but values should be done lazily where possible.
    """

    _original: Optional[Node] = None

    def __init__(
        self,
        original: Optional[Node],
        stream: Optional[YamlStream],
        annealed: bool = False,
    ):
        self._original = original
        self._stream = stream
        self._annealed = original is None

    @property
    def start_byte(self) -> int:
        if self._annealed:
            raise RuntimeError("start_byte of annealed item should not be accessed")
        assert self._original is not None
        return self._original.start_byte

    @property
    def end_byte(self) -> int:
        if self._annealed:
            raise RuntimeError("end_byte of annealed item should not be accessed")
        assert self._original is not None
        return self._original.end_byte

    @classmethod
    @abc.abstractmethod
    def from_yaml(cls, node: Node, stream: YamlStream) -> "Item":
        pass

    def anneal(self, initial: bool = True) -> None:
        if self._annealed:
            return

        if initial and self._original and self._stream:
            self._stream.edit(self, self)

        self._annealed = True

    @abc.abstractmethod
    def to_string(self) -> str:
        pass
