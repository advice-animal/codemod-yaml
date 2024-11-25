from __future__ import annotations

import sys
from pathlib import Path

from typing import Any, Optional

from codemod_yaml import parse

USAGE = """
Run like:

```
cyq foo.0.bar /path/to/file
```

which will print `stream["foo"][0]["bar"]` for each file
"""


def main(args: Optional[list[str]] = None) -> int:
    if args is None:
        args = sys.argv[1:]

    if len(args) < 2:
        print(USAGE)
        return 1

    expr = args[0]
    files = args[1:]

    exit_code = 0
    for f in files:
        print(f)
        try:
            result = repr(eval_expr(f, expr))
        except Exception as e:
            exit_code |= 1
            result = repr(e)
        print("  ", expr, "=", result)

    return exit_code


def eval_expr(filename: str, expression: str) -> Any:
    obj = parse(Path(filename).read_bytes())

    for piece in expression.split("."):
        if piece.isdigit():
            obj = obj[int(piece)]
        else:
            obj = obj[piece]
    return obj


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
