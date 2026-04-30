"""Map raw Lark parse trees back to rich morphological information.

Lark trees will contain category labels such as `P1`, `P3`, and `VP`. The CLI
and any future API need richer output: selected surface token, root, feature
bundle, and discarded alternative readings.

This module will own that reconstruction step.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .morphology import MorphState, TokenNode


@dataclass(frozen=True)
class MappedNode:
    """A parser-output node enriched with morphology.

    Planned fields:
    - `label`: syntactic label from the parse tree.
    - `surface`: original token text when the node corresponds to a token.
    - `state`: selected morphological state for token leaves.
    - `discarded`: alternative states from the same `TokenNode`.
    - `children`: recursively mapped child nodes.
    """

    label: str
    surface: str | None = None
    state: MorphState | None = None
    discarded: list[MorphState] = field(default_factory=list)
    children: list["MappedNode"] = field(default_factory=list)


class TreeMapper:
    """Attach morphology and source-token details to accepted parse trees.

    Planned implementation:
    - Walk the accepted Lark tree in terminal order.
    - Align category leaves with the selected states from a `ParseCandidate`.
    - Attach each `MorphState` and original `TokenNode.surface`.
    - Record unselected states as discarded alternatives for CLI reporting.
    - Preserve nested phrase structure so derivation trees remain readable.
    """

    def map_tree(
        self,
        tree: Any,
        nodes: list[TokenNode],
        selected_states: list[MorphState],
    ) -> MappedNode:
        """Return a morphology-enriched representation of *tree*.

        The future implementation should validate that the number and order of
        selected states matches the terminal leaves in the parse tree.
        """

        raise NotImplementedError("TreeMapper.map_tree is not implemented yet.")

