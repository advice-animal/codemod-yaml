"""
Run like:

```
cyq foo.0.bar /path/to/file
```

which will print `stream["foo"][0]["bar"]` for each file
"""

import sys
from pathlib import Path
from typing import Any

from codemod_yaml import parse


def main() -> None:
    expr = sys.argv[1]
    files = sys.argv[2:]

    exit_code = 0
    for f in files:
        print(f)
        try:
            result = repr(eval_expr(f, expr))
        except Exception as e:
            exit_code |= 1
            result = repr(e)
        print("  ", expr, "=", result)

    sys.exit(exit_code)


def eval_expr(filename: str, expression: str) -> Any:
    obj = parse(Path(filename).read_bytes())

    for piece in expression.split("."):
        if piece.isdigit():
            obj = obj[int(piece)]
        else:
            obj = obj[piece]
    return obj


if __name__ == "__main__":
    main()
