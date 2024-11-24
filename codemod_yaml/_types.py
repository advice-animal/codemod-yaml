# Largely verbatim (including comment explanation) from tomlkit/_types.py (MIT)

from __future__ import annotations

from typing import Any, TYPE_CHECKING, TypeVar


WT = TypeVar("WT", bound="WrapperType")

if TYPE_CHECKING:  # pragma: no cover
    # Define _CustomList and _CustomDict as a workaround for:
    # https://github.com/python/mypy/issues/11427
    #
    # According to this issue, the typeshed contains a "lie"
    # (it adds MutableSequence to the ancestry of list and MutableMapping to
    # the ancestry of dict) which completely messes with the type inference for
    # Table, InlineTable, Array and Container.
    #
    # Importing from builtins is preferred over simple assignment, see issues:
    # https://github.com/python/mypy/issues/8715
    # https://github.com/python/mypy/issues/10068
    from builtins import (
        dict as _CustomDict,
        float as _CustomFloat,
        int as _CustomInt,
        list as _CustomList,
    )
    from typing import ParamSpec, Protocol

    P = ParamSpec("P")

    class WrapperType(Protocol):
        def _new(self: WT, value: Any) -> WT: ...

else:
    from collections.abc import MutableMapping, MutableSequence
    from numbers import Integral, Real

    class _CustomList(MutableSequence, list):
        """Adds MutableSequence mixin while pretending to be a builtin list"""

        def __add__(self, other):
            new_list = self.copy()
            new_list.extend(other)
            return new_list

        def __iadd__(self, other):
            self.extend(other)
            return self

    class _CustomDict(MutableMapping, dict):
        """Adds MutableMapping mixin while pretending to be a builtin dict"""

        def __or__(self, other):
            new_dict = self.copy()
            new_dict.update(other)
            return new_dict

        def __ior__(self, other):
            self.update(other)
            return self

    class _CustomInt(Integral, int):
        """Adds Integral mixin while pretending to be a builtin int"""

    class _CustomFloat(Real, float):
        """Adds Real mixin while pretending to be a builtin float"""


__all__ = ["_CustomDict", "_CustomList", "_CustomFloat", "_CustomInt"]
