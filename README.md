# codemod-yaml

This library is for making targeted edits to YAML documents.  The core design goal is:

1. Only change lines with *data* changes.

While you can't edit all YAML constructs, you can generally replace them and
roundtrip them thanks to tree-sitter-yaml.

This was roughly inspired by `pyupgrade` which combined AST-based parsing with
more low-level edits.

# Basic Usage

```py
from codemod_yaml import parse
stream = parse(somepath.read_bytes())
if stream["version"] == ["2.7"]:
    stream["version"][:] = ["3.6", "3.13"]
somepath.write_bytes(stream.text)
```

# Supported
[x] round-tripping unedited sections verbatim
[x] any valid yaml _after_ where you're editing
[x] block maps with string keys
[x] block sequences
[x] python str/float/list/dict

# Version Compat

Usage of this library should work back to 3.7, but development (and mypy
compatibility) only on 3.10-3.12.  Linting requires 3.12 for full fidelity.

# Versioning

This library follows [meanver](https://meanver.org/) which basically means
[semver](https://semver.org/) along with a promise to rename when the major
version changes.

# License

codemod-yaml is copyright [Tim Hatch](https://timhatch.com/), and licensed under
the MIT license.  See the `LICENSE` file for details.
