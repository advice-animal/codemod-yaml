from __future__ import annotations

from typing import Optional

from ..style import YamlStyle

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
    def __init__(self, value: BoxedPy, yaml_style: Optional[YamlStyle] = None) -> None:
        super().__init__(value)
        self.yaml_style = yaml_style or YamlStyle()

    def to_str(self) -> str:
        # TODO this ought to be bytes, and wrap
        return (  # type: ignore[no-any-return]
            self.yaml_style.sequence_whitespace_before_dash
            + "-"
            + self.yaml_style.sequence_whitespace_after_dash
            + self.value.to_str()
            + "\n"
        )
