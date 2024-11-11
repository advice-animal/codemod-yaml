import ast
from dataclasses import dataclass

from .base import BaseSurrogate, BaseYaml


@dataclass
class YamlIntegerScalar(BaseYaml):
    string_value: str = ""
    value: int = 0

    def __repr__(self) -> str:
        return self.value

    def __int__(self) -> int:
        return self.value

    def __post_init__(self) -> None:
        self.string_value = self.node.text.decode("utf-8")
        t = self.string_value
        if t[0] == "0" and t[:2] not in ("0o", "0x") and t != "0":
            t = "0o" + t[1:]
        self.value = ast.literal_eval(t)

    def __eq__(self, other: int) -> bool:
        return self.value == other

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass
class SurrogateIntegerScalar(BaseSurrogate):
    value: int

    def to_bytes(self) -> bytes:
        return str(self.value).encode("utf-8")


@dataclass
class YamlStringScalar(BaseYaml):
    value: str = ""

    def __repr__(self) -> str:
        return self.value

    def __str__(self) -> str:
        return self.value

    def __post_init__(self) -> None:
        self.value = self.node.text.decode("utf-8")

    def __eq__(self, other: str) -> bool:
        return self.value == other

    def __hash__(self) -> int:
        return hash(self.value)

    def record_change(self, new_bytes: bytes) -> None:
        # cookie = ...
        self.stream.record_edit(self.node, new_bytes)


@dataclass
class SurrogateStringScalar(BaseSurrogate):
    value: str

    def to_bytes(self) -> bytes:
        return self.value.encode("utf-8")
