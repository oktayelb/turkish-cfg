from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _load_parser_tools():
    if __package__ in {None, ""}:
        from turkish_cfg.parser import CFGParser
        from turkish_cfg.tree_mapper import TreeMapper
    else:
        from .parser import CFGParser
        from .tree_mapper import TreeMapper
    return CFGParser, TreeMapper


def format_result(sentence: str) -> str:
    CFGParser, TreeMapper = _load_parser_tools()
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


def run_interactive() -> int:
    print("Turkish CFG interactive parser")
    print("Enter a sentence to parse. Type 'quit' or 'exit' to stop.")

    while True:
        try:
            sentence = input("\nsentence> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        if not sentence:
            continue
        if sentence.lower() in {"quit", "exit", ":q"}:
            return 0

        try:
            print(format_result(sentence))
        except Exception as exc:
            print(f"ERROR: {exc}")


def main(argv: list[str] | None = None) -> int:
    arg_parser = argparse.ArgumentParser(description="Parse Turkish sentences with a Savyar-pruned CFG.")
    arg_parser.add_argument("sentence", nargs="*", help="Sentence to parse. Omit to start interactive mode.")
    args = arg_parser.parse_args(argv)

    if not args.sentence:
        return run_interactive()

    print(format_result(" ".join(args.sentence)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
