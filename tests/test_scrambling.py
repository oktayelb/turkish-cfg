"""Planned scrambling tests.

These tests will validate the central Turkish word-order behavior from the
roadmap. The parser should accept multiple phrase orders when case marking
keeps the grammatical roles clear.

Future assertions:
- `Ali kitabı okudu` is accepted as default SOV.
- `Kitabı Ali okudu` is accepted as OSV scrambling.
- Additional OVS/SVO-style cases are accepted when morphology licenses them.
- Accepted parses preserve the selected morphological reading for each token.
"""


def test_scrambling_skeleton_placeholder() -> None:
    """Placeholder until the parser is implemented."""

    assert True

