from typing import Any, Dict, Union

from ..py import BoxedPy, boxpy

from ..yaml import BoxedYaml, boxyaml, register

__all__ = ["YamlBlockMapping", "YamlBlockMappingPair"]


@register("block_node.block_mapping")
class YamlBlockMapping(BoxedYaml):
    # block_mapping > block_mapping_pair > key/value flow_node/block_node > $value

    # Keys can be of any scalar type, but for now just treat them as strings.
    _cache: Dict[str, Union["YamlBlockMappingPair", None]]

    def __post_init__(self) -> None:
        self._cache = {}

    def __getitem__(self, key: str) -> Union[BoxedPy, BoxedYaml]:
        if key in self._cache:
            if self._cache[key] is not None:
                return self._cache[key].value  # type: ignore[union-attr]
            else:
                raise KeyError(key)

        for pair in self.node.children[0].children:
            print(repr(pair.children))
            assert pair.type == "block_mapping_pair"
            pair_key = str(boxyaml(node=pair.children[0], stream=self.stream))
            if key == pair_key:
                kv = boxyaml(node=pair, stream=self.stream)
                assert isinstance(kv, YamlBlockMappingPair)
                self._cache[pair_key] = kv
                return kv.value
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        py_item = boxpy(value)
        if isinstance(self[key], BoxedYaml):
            self.stream.edit(self[key], py_item)  # type: ignore[arg-type]
        else:
            raise ValueError(self[key])  # TODO append
        c = self._cache[key]
        assert c is not None  # TODO re-add deleted items
        c.value = py_item

    def __delitem__(self, key: str) -> None:
        # TODO if self.key[cookie], self._stream.record_delete(cookie)
        self[key]
        c = self._cache[key]
        if isinstance(c, BoxedYaml):
            self.stream.edit(c, None)
        self._cache[key] = None


@register("block_mapping_pair")
class YamlBlockMappingPair(BoxedYaml):
    key: BoxedYaml
    value: Union[BoxedPy, BoxedYaml]

    def __post_init__(self) -> None:
        self.key = boxyaml(node=self.node.children[0], stream=self.stream)
        self.value = boxyaml(node=self.node.children[2], stream=self.stream)

    @property
    def start_byte(self) -> int:
        expected_indent = self.node.start_point.column
        leading_whitespace = self.stream._original_bytes[
            self.node.start_byte - expected_indent : self.node.start_byte
        ]
        assert (
            leading_whitespace == b" " * expected_indent
        )  # can't handle same-line block like "- - a" yet
        return self.node.start_byte - expected_indent

    @property
    def end_byte(self) -> int:
        # TODO conditional
        return self.node.end_byte + 1
