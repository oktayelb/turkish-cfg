from __future__ import annotations

import json
import sys
from pathlib import Path

from .morphology import _DirectSavyar
from .tokenizer import Token


def main() -> int:
    request = json.loads(sys.stdin.read())
    tokens = [Token(**token) for token in request["tokens"]]
    direct = _DirectSavyar(Path(request["savyar_dir"]))
    payload = direct.analyze(tokens, int(request.get("top_k", 3)))
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
