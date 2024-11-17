import enum
import re

from ..base_types import UserInt, UserStr

from . import BoxedPy, register


class QuoteStyle(enum.IntEnum):
    AUTO = 0  # Prefer double quotes, but use single if necessary
    SINGLE = 1
    DOUBLE = 2
    BARE = 3


BARE_STRING_OK = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]+$")

__all__ = ["PyScalarString", "PyScalarInt", "QuoteStyle"]


@register(int)
class PyScalarInt(BoxedPy, UserInt):

    value: int

    # TODO support base or some other style pref
    def __init__(self, value: int):
        super().__init__(value)

    def to_str(self) -> str:
        return str(self.value)


@register(str)
class PyScalarString(BoxedPy, UserStr):
    """
    This wraps all simple Python strings.

    Use the optional `quote_style` param to control quoting preferences.
    """

    value: str
    quote_style: QuoteStyle

    def __init__(self, value: str, quote_style: QuoteStyle = QuoteStyle.AUTO):
        super().__init__(value)
        self.quote_style = quote_style

    def to_str(self) -> str:
        quote_style = self.quote_style
        if quote_style == QuoteStyle.AUTO:
            if '"' in self.value:
                quote_style = QuoteStyle.SINGLE
            else:
                quote_style = QuoteStyle.DOUBLE

        if quote_style == QuoteStyle.SINGLE:
            if "'" in self.value:
                raise ValueError(
                    f"{self.quote_style} -> {quote_style} cannot represent {self.value!r}"
                )
            return f"'{self.value}'"  # TODO escaping
        elif quote_style == QuoteStyle.DOUBLE:
            if '"' in self.value:
                raise ValueError(
                    f"{self.quote_style} -> {quote_style} cannot represent {self.value!r}"
                )
            return f'"{self.value}"'  # TODO escaping
        elif quote_style == QuoteStyle.BARE:
            if not BARE_STRING_OK.match(self.value):
                raise ValueError(f"{self.value} cannot be represented as a bare string")
            return self.value
        else:
            raise ValueError(f"{self.quote_style} -> {quote_style} unknown")
