"""Planned morphology tests.

These tests will verify that ambiguous Turkish surface forms produce multiple
correct `MorphState` readings before syntax chooses among them.

Future assertions:
- `kitabı` includes an accusative `P3` reading rooted at `kitap`.
- `kitabı` also includes nominative possessive readings where appropriate.
- finite verbs such as `okudu` produce a `VP` reading with tense and agreement.
- unknown words produce structured diagnostics instead of crashing.
"""


def test_morphology_skeleton_placeholder() -> None:
    """Placeholder until the morphology analyzer is implemented."""

    assert True

