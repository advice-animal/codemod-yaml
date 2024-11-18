# These are because I haven't figured out how to overwrite `__init__` on these classes yet.
from typing import Iterator


class UserStr:
    value: str = ""

    def __repr__(self) -> str:
        return self.value

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        return self.value == other

    def __hash__(self) -> int:
        return hash(self.value)


class UserInt:
    value: int = -1

    def __repr__(self) -> str:
        return str(self.value)

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        return self.value == other

    def __hash__(self) -> int:
        return hash(self.value)


class UserList:
    _items: list[object]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[object]:
        return iter(self._items)

    def __eq__(self, other: object) -> bool:
        if len(self) != len(other):  # type: ignore[arg-type]
            return False
        for a, b in zip(self, other):  # type: ignore[call-overload]
            if a != b:
                return False
        return True
