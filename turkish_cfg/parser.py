"""Lark parser wrapper and morphology-lattice parsing plan.

The parser layer will sit between the morphology analyzer and tree mapper. Its
main job is to convert a sequence of `TokenNode` objects into category paths,
feed those paths to Lark, and retain only accepted derivations.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .morphology import TokenNode


@dataclass(frozen=True)
class ParseCandidate:
    """A single attempted path through the morphology lattice.

    Planned fields:
    - `categories`: the CFG terminal sequence submitted to Lark.
    - `states`: the selected `MorphState` objects, one per source token.
    - `tree`: the raw Lark tree if the candidate parses successfully.
    - `error`: parser error details when the candidate is rejected.
    """

    categories: tuple[str, ...]
    states: tuple[Any, ...]
    tree: Any | None = None
    error: Exception | None = None


class CFGParser:
    """Parse category sequences generated from a Turkish morphology lattice.

    Planned implementation:
    - Load `grammar.lark` from the package or from a supplied path.
    - Initialize `lark.Lark` with `parser="earley"` and
      `ambiguity="explicit"` to support ambiguous category sequences.
    - Expand the token lattice into all category/state combinations. This is
      acceptable for the first prototype but should eventually be pruned to
      avoid combinatorial growth.
    - Feed each category sequence to Lark as a whitespace-separated string.
    - Collect valid parse trees and rejected candidates.
    - Preserve enough bookkeeping for `TreeMapper` to reattach roots, features,
      and discarded alternatives.
    """

    def __init__(self, grammar_file: str | Path | None = None) -> None:
        """Prepare a parser for the configured grammar file.

        Future implementation will load the grammar and construct the Lark
        parser here. The default path should point to `turkish_cfg/grammar.lark`.
        """

        self.grammar_file = (
            Path(grammar_file)
            if grammar_file is not None
            else Path(__file__).with_name("grammar.lark")
        )
        raise NotImplementedError("CFGParser initialization is not implemented yet.")

    def parse_lattice(self, nodes: list[TokenNode]) -> list[ParseCandidate]:
        """Parse every valid path through a list of token nodes.

        Planned algorithm:
        1. Compute the Cartesian product of `node.states` for all nodes.
        2. Convert each product into a category sequence such as
           `P1 P3 VP` or `P1 P2 VP`.
        3. Submit the sequence to Lark.
        4. Wrap successful parses in `ParseCandidate(tree=...)`.
        5. Wrap rejected parses with their parser exception for diagnostics.
        6. Return accepted candidates first, or expose separate accepted and
           rejected collections via a richer result object.
        """

        raise NotImplementedError("CFGParser.parse_lattice is not implemented yet.")

