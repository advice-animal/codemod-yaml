# codemod-yaml

This library is for making targeted edits to YAML documents, with the aim of
keeping all non-edited lines verbatim.

It does not support *editing* all YAML constructs, but should support
*round-tripping* them by virtue of using tree-sitter-yaml for the actual
parsing.

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
