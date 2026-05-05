from __future__ import annotations

import argparse

from .parser import CFGParser
from .tree_mapper import TreeMapper


def format_result(sentence: str) -> str:
    parser = CFGParser()
    result = parser.parse(sentence)
    lines: list[str] = []

    if result.accepted:
        count = len(result.derivations)
        lines.append(f"STATUS: ACCEPTED ({count} valid derivation{'s' if count != 1 else ''} found)")
    else:
        lines.append("STATUS: REJECTED")

    lines.append("")
    lines.append("--- LATTICE RESOLUTION ---")
    if result.best:
        selected = result.best.states
        for token, state in zip(result.tokens, selected):
            raw = state.features.get("raw_savyar") or state.root
            lines.append(f"{token:<12} -> Selected: {state.category:<2} Root: {state.root:<12} Raw: {raw}")
    else:
        for node in result.lattice:
            categories = ", ".join(state.category for state in node.states) or "(none)"
            lines.append(f"{node.surface:<12} -> Alternatives: {categories}")

    if result.discarded:
        lines.append("")
        lines.append("--- DISCARDED CATEGORY SEQUENCES ---")
        for categories in result.discarded[:10]:
            lines.append(" ".join(categories))

    lines.append("")
    lines.append("--- DERIVATION TREE ---")
    lines.append(TreeMapper().render(result))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    arg_parser = argparse.ArgumentParser(description="Parse Turkish sentences with a Savyar-pruned CFG.")
    arg_parser.add_argument("sentence", nargs="+", help="Sentence to parse")
    args = arg_parser.parse_args(argv)
    print(format_result(" ".join(args.sentence)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
