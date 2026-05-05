from __future__ import annotations

from dataclasses import dataclass
import itertools
from pathlib import Path
from typing import Iterable

from lark import Lark, Tree
from lark.exceptions import LarkError

from .morphology import MorphState, SavyarInterface, TokenNode
from .tokenizer import TurkishTokenizer

@dataclass(frozen=True)
class Derivation:
    categories: tuple[str, ...]
    states: tuple[MorphState, ...]
    tree: Tree
    score: float

@dataclass(frozen=True)
class ParseResult:
    accepted: bool
    tokens: list[str]
    lattice: list[TokenNode]
    derivations: list[Derivation]
    discarded: list[tuple[str, ...]]

    @property
    def best(self) -> Derivation | None:
        return self.derivations[0] if self.derivations else None

class CFGParser:
    def __init__(
        self,
        grammar_file: str | Path | None = None,
        analyzer: SavyarInterface | None = None,
        tokenizer: TurkishTokenizer | None = None,
    ) -> None:
        grammar_path = Path(grammar_file or Path(__file__).with_name("grammar.lark"))
        self.parser = Lark(
            grammar_path.read_text(encoding="utf-8"),
            start="start",
            parser="earley",
            ambiguity="explicit",
        )
        self.analyzer = analyzer or SavyarInterface()
        self.tokenizer = tokenizer or TurkishTokenizer()

    def parse(self, sentence: str) -> ParseResult:
        tokens = self.tokenizer.tokenize(sentence)
        lattice = self.analyzer.analyze(tokens)
        return self.parse_lattice(lattice)

    def parse_lattice(self, lattice: list[TokenNode]) -> ParseResult:
        state_lists = [node.states for node in lattice]
        if not state_lists or any(not states for states in state_lists):
            return ParseResult(False, [node.surface for node in lattice], lattice, [], [])

        # Sort individual token states by score descending to prioritize highly probable paths
        sorted_state_lists = [
            sorted(states, key=lambda s: s.score - (s.rank * 0.001), reverse=True) 
            for states in state_lists
        ]

        accepted: list[Derivation] = []
        discarded: list[tuple[str, ...]] = []

        # Bound the Cartesian product to prevent combinatorial explosion (O(k^N) hang)
        MAX_PATHS = 1500
        bounded_product = itertools.islice(itertools.product(*sorted_state_lists), MAX_PATHS)
        for states in bounded_product:
            categories = tuple(state.category for state in states)
            try:
                tree = self.parser.parse(" ".join(categories))
            except LarkError:
                discarded.append(categories)
                continue

            accepted.append(
                Derivation(
                    categories=categories,
                    states=tuple(states),
                    tree=tree,
                    score=self._score_states(states),
                )
            )

        accepted.sort(key=lambda derivation: derivation.score, reverse=True)
        return ParseResult(
            bool(accepted),
            [node.surface for node in lattice],
            lattice,
            accepted,
            discarded,
        )

    def _score_states(self, states: Iterable[MorphState]) -> float:
        state_list = list(states)
        score = sum(state.score - (state.rank * 0.001) for state in state_list)
        categories = [state.category for state in state_list]
        score += categories.count("P3") * 0.7
        for index, category in enumerate(categories[:-1]):
            if categories[index + 1] == "VP":
                if category == "P3":
                    score += 1.0
                elif category == "P2":
                    score += 0.5
        return score