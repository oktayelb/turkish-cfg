"""Morphological lattice types and analyzer skeleton.

Turkish morphology is highly ambiguous. A single surface token can correspond
to several syntactic categories and feature bundles. For example, "kitabı" may
be an accusative object (`P3`) or a nominative possessive noun phrase (`P1`),
depending on the sentence.

This module will provide:
- `MorphState`: one possible reading of a token.
- `TokenNode`: the surface token plus all readings for that token.
- `MorphologicalAnalyzer`: the component that builds a token lattice.

The first prototype is expected to be rule-based and small. It should cover the
roadmap examples before growing into a broader Turkish morphotactic analyzer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MorphState:
    """One possible morphological interpretation for a token.

    Planned fields:
    - `category`: CFG-facing terminal category such as `P1`, `P2`, `P3`, `VP`,
      or `MI`.
    - `root`: dictionary or stem form, such as `kitap` for `kitabı`.
    - `features`: structured details used by later disambiguation and output,
      including case, number, person, tense, polarity, possessive markers, and
      clitic metadata.
    """

    category: str
    root: str
    features: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TokenNode:
    """A single surface token and every possible analysis for it.

    Future parser flow:
    - The tokenizer yields surface tokens.
    - The analyzer turns each surface token into a `TokenNode`.
    - The parser expands the list of nodes into category permutations.
    - Valid parse trees identify which state from each node was selected.
    """

    surface: str
    states: list[MorphState]


class MorphologicalAnalyzer:
    """Build a lattice of possible Turkish morphological readings.

    Planned implementation layers:
    - A minimal hand-written lexicon for early examples: proper nouns, common
      nouns such as `kitap`, and verbs such as `oku`.
    - Case suffix recognition for nominative, accusative, dative, locative,
      ablative, and instrumental phrases.
    - Distinction between `P1` nominative subject and `P2` nominative indefinite
      object. Both may be unmarked, but grammar constraints decide whether a
      `P2` reading is valid.
    - Verb phrase detection with tense, aspect, mood, polarity, and agreement
      features.
    - Question clitic mapping to the `MI` category after tokenizer validation.
    - Later support for derivational boundaries, inflectional groups, and
      recursive genitive-possessive izafet chains.
    """

    def analyze(self, token: str) -> TokenNode:
        """Return every possible morphological reading for *token*.

        Planned behavior for early prototype examples:
        - `Ali` should produce at least a proper-noun `P1` reading.
        - `kitap` should produce a nominative noun reading and, in object
          position, a `P2` indefinite object candidate.
        - `kitabı` should produce competing `P3`, `P1`, and possibly `P2`
          readings so the CFG can disambiguate.
        - `okudu` should produce a finite `VP` reading with root `oku`, past
          tense, and third-person singular agreement.

        This method is intentionally not implemented yet.
        """

        raise NotImplementedError("MorphologicalAnalyzer.analyze is not implemented yet.")

    def analyze_sentence(self, tokens: list[str]) -> list[TokenNode]:
        """Analyze every token and return the full token lattice.

        Future implementation should call `analyze` for each token, collect
        diagnostics for unknown words, and preserve the original token order.
        """

        raise NotImplementedError(
            "MorphologicalAnalyzer.analyze_sentence is not implemented yet."
        )

