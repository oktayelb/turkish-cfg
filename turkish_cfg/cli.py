"""Command-line interface for the planned Turkish CFG parser.

The CLI will eventually provide the end-to-end workflow:
raw sentence -> tokenizer -> morphology lattice -> CFG parser -> mapped tree.

Expected first prototype command:

    python -m turkish_cfg.cli "Ali kitabı okudu"

Expected output shape:
- accepted or rejected status
- selected morphological reading per token
- discarded alternatives
- derivation tree
"""

from __future__ import annotations

import argparse


def build_arg_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser.

    Future options may include:
    - `--show-rejected` to print rejected lattice paths.
    - `--json` to emit machine-readable parse results.
    - `--grammar` to use an experimental grammar file.
    - `--trace` to show tokenizer and morphology diagnostics.
    """

    parser = argparse.ArgumentParser(
        prog="turkish-cfg",
        description="Parse Turkish sentences with a planned rule-based CFG parser.",
    )
    parser.add_argument("sentence", help="Turkish sentence to parse.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Planned runtime flow:
    1. Parse command-line arguments.
    2. Tokenize the sentence with `TurkishTokenizer`.
    3. Analyze tokens with `MorphologicalAnalyzer`.
    4. Parse the lattice with `CFGParser`.
    5. Map accepted trees with `TreeMapper`.
    6. Print a human-readable report.

    The skeleton currently stops after argument parsing.
    """

    build_arg_parser().parse_args(argv)
    raise NotImplementedError("The turkish-cfg CLI is not implemented yet.")


if __name__ == "__main__":
    raise SystemExit(main())

