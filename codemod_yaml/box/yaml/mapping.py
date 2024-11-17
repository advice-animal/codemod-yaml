from typing import Dict, Union

from ..py import BoxedPy

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


@register("block_mapping_pair")
class YamlBlockMappingPair(BoxedYaml):
    def __post_init__(self) -> None:
        self.key = boxyaml(node=self.node.children[0], stream=self.stream)
        self.value = boxyaml(node=self.node.children[2], stream=self.stream)
