from __future__ import annotations

from turkish_cfg.morphology import MorphState, TokenNode
from turkish_cfg.parser import CFGParser


class FakeAnalyzer:
    def __init__(self, lattice: list[TokenNode]) -> None:
        self.lattice = lattice

    def analyze(self, tokens):
        return self.lattice


def node(surface: str, *categories: str) -> TokenNode:
    return TokenNode(
        surface=surface,
        normalized=surface.lower(),
        states=[
            MorphState(category=category, root=surface.lower(), features={"raw_savyar": surface.lower()})
            for category in categories
        ],
    )


def parse_lattice(lattice: list[TokenNode]):
    parser = CFGParser(analyzer=FakeAnalyzer(lattice))
    return parser.parse_lattice(lattice)


def test_valid_scrambling_orders_accept():
    assert parse_lattice([node("Ali", "P1"), node("kitabı", "P3"), node("okudu", "VP")]).accepted
    assert parse_lattice([node("Kitabı", "P3"), node("Ali", "P1"), node("okudu", "VP")]).accepted


def test_p2_must_be_adjacent_to_verb():
    assert parse_lattice([node("Ali", "P1"), node("kitap", "P2"), node("okudu", "VP")]).accepted
    assert not parse_lattice([node("Kitap", "P2"), node("Ali", "P1"), node("okudu", "VP")]).accepted


def test_cfg_disambiguates_lattice():
    result = parse_lattice([node("Kitabı", "P1", "P3"), node("okudu", "VP")])
    assert result.accepted
    assert ("P3", "VP") in [derivation.categories for derivation in result.derivations]
