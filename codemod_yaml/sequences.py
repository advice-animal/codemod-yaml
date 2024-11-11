from dataclasses import dataclass, field
from typing import Dict

from .base import BaseYaml
from .convert import wrap


@dataclass
class YamlBlockSequence(BaseYaml):
    # block_sequence > block_sequence_item > flow_node > $value
    _cache: Dict[int, BaseYaml] = field(default_factory=dict)

    def __getitem__(self, index: int) -> BaseYaml:
        if index in self._cache:
            return self._cache[index]

        # node is block_sequence_item
        node = self.node.children[0].children[index]
        # node.children[0] is the "-"
        value = wrap(node.children[1], self.stream)
        self._cache[index] = value
        return value
