"""Planned grammar-constraint tests.

The first strict constraint is that `P2`, the unmarked indefinite object, must
immediately precede the verb phrase. This distinguishes valid sentences such as
`Ali kitap okudu` from invalid orders where `kitap` is separated from `okudu`.

Future assertions:
- `Ali kitap okudu` is accepted with `kitap` selected as `P2`.
- `Kitap Ali okudu` is rejected when `kitap` can only satisfy `P2`.
- `P2` should not be hidden inside generic phrase scrambling.
- parser diagnostics explain which lattice paths were discarded.
"""


def test_constraints_skeleton_placeholder() -> None:
    """Placeholder until the P2 constraint is implemented."""

    assert True

