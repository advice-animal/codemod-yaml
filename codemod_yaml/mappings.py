from dataclasses import dataclass, field
from typing import Any, Dict, Union

from .base import _Erasure, BaseYaml, ERASURE
from .convert import wrap, wrap_native


@dataclass
class YamlBlockMapping(BaseYaml):
    # block_mapping > block_mapping_pair > key/value flow_node/block_node > $value
    _cache: Dict[Any, Union[BaseYaml, _Erasure]] = field(default_factory=dict)

    def __getitem__(self, key: str) -> BaseYaml:
        if key in self._cache:
            if self._cache[key] is not ERASURE:
                return self._cache[key]
            else:
                raise KeyError(key)

        for pair in self.node.children[0].children:
            print(repr(pair.children))
            assert pair.type == "block_mapping_pair"
            pair_key = str(wrap(pair.children[0], self.stream))
            if key == pair_key:
                t = wrap(pair.children[2], self.stream)
                self._cache[pair_key] = t
                return t
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        yaml_value = wrap_native(value, self.stream)
        try:
            self[key].record_change(yaml_value.to_bytes())
            self._cache[key] = yaml_value
        except KeyError:
            pass

    def __delitem__(self, key: str) -> None:
        self[key]
        self[key].record_change(b"")
        self._cache[key] = ERASURE


# @dataclass
# class YamlFlowMapping(BaseYaml):
#     def __getitem__(self, key):
#         ...
#         for pair in self.node.children:
#             assert pair.type == "flow_pair"
#
