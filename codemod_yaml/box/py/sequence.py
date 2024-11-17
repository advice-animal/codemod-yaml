from __future__ import annotations

from . import BoxedPy, boxpy

__all__ = [
    "PyBlockSequence",
    "PyBlockSequenceItem",
]


class PyBlockSequence(BoxedPy):
    register_py_type = list

    _items: list[PyBlockSequenceItem]

    def __post_init__(self) -> None:
        self._items = []
        for child in self.value.children:
            self._items.append(PyBlockSequenceItem(boxpy(child)))

    def to_bytes(self) -> bytes:
        buf = []
        for item in self._items:
            buf.append(item.to_bytes())
        if buf[-1][-1:] != b"\n":
            buf.append(b"\n")
        return b"".join(buf)


class PyBlockSequenceItem(BoxedPy):

    def to_str(self) -> str:
        # TODO this ought to be bytes, and wrap
        return "- " + self.value.to_str() + "\n"  # type: ignore[no-any-return]
