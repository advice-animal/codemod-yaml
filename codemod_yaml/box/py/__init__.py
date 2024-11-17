from __future__ import annotations

from typing import Any, Callable


class BoxedPy:
    """
    Boxed version of a python object.  Does not automatically stage an edit --
    the parent container should do so, after copying style preferences.
    """

    value: Any
    base_indent: int

    def __init__(self, value: Any):
        self.value = value
        # self.stream = stream
        #: Not all BoxedPy need an indent (only block ones)
        self.base_indent = 0
        #: Not all BoxedPy need to know their style; this looks up the global default if necessary.
        self.style = None

        self.__post_init__()

    def __post_init__(self) -> None:
        pass

    def to_bytes(self) -> bytes:
        return self.to_str().encode("utf-8")

    def to_str(self) -> str:  # pragma: no cover
        raise NotImplementedError


def boxpy(obj: object, **kwargs: Any) -> BoxedPy:
    """
    Upgrades a Python object (of known type) to a BoxedPy object.

    These objects have a `.to_bytes()` method that is used to serialize them when used in a `PendingEdit`.
    """
    if isinstance(obj, BoxedPy):
        return obj

    typ = REGISTRY_PY.get(type(obj))
    if typ is None:
        raise ValueError(f"Can't convert {obj} of {type(obj)}")
    return typ(obj, **kwargs)


REGISTRY_PY: dict[type[object], type[BoxedPy]] = {}


def register(typ: type[object]) -> Callable[[type[BoxedPy]], type[BoxedPy]]:
    def callable(cls: type[BoxedPy]) -> type[BoxedPy]:
        REGISTRY_PY[typ] = cls
        return cls

    return callable
