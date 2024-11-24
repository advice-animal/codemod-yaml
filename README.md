# codemod-yaml

This library makes surgical edits to YAML documents, based on tree-sitter and
inspired by tomlkit and pyupgrade.  Preserves _all_ whitespace and formatting
on lines that don't require changes, and generally within a line as well, so
you can make minimal diffs in your codemod tools.

# Basic Usage

```py
from codemod_yaml import parse
stream = parse(somepath.read_bytes())
if stream["version"] == ["2.7"]:
    stream["version"][:] = ["3.6", "3.13"]
somepath.write_bytes(stream.text)
```

# Version Compat

Usage of this library should work back to 3.9 (because of the tree-sitter dep),
but development (and mypy compatibility) only on 3.10-3.12.  Linting requires
3.12+ for full fidelity.

# Versioning

This library follows [meanver](https://meanver.org/) which basically means
[semver](https://semver.org/) along with a promise to rename when the major
version changes.

# License

codemod-yaml is copyright [Tim Hatch](https://timhatch.com/), and licensed under
the MIT license.  See the `LICENSE` file for details.
