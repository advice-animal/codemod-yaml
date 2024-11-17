try:
    from ._version import __version__
except ImportError:  # pragma: no cover
    __version__ = "dev"

from .box.py import boxpy
from .box.py.scalar import PyScalarInt, PyScalarString, QuoteStyle

from .box.yaml import boxyaml
from .box.yaml.mapping import YamlBlockMapping, YamlBlockMappingPair
from .box.yaml.scalar import (
    YamlBareScalarString,
    YamlBlockScalarString,
    YamlDoubleQuoteScalarString,
    YamlScalarInt,
    YamlSingleQuoteScalarString,
)
from .box.yaml.sequence import YamlBlockSequence, YamlBlockSequenceItem
from .parser import parse, parse_str, YamlStream

__all__ = [
    "parse",
    "parse_str",
    "YamlStream",
    "boxpy",
    "boxyaml",
    "YamlBareScalarString",
    "YamlBlockScalarString",
    "YamlDoubleQuoteScalarString",
    "YamlSingleQuoteScalarString",
    "YamlScalarInt",
    "YamlBlockSequence",
    "YamlBlockSequenceItem",
    "YamlBlockMapping",
    "YamlBlockMappingPair",
    "PyScalarString",
    "PyScalarInt",
    "QuoteStyle",
]
