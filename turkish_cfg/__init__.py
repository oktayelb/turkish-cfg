"""Morphology-aware CFG parser for Turkish."""

__all__ = ["CFGParser", "ParseResult"]


def __getattr__(name: str):
    if name in __all__:
        from .parser import CFGParser, ParseResult

        return {"CFGParser": CFGParser, "ParseResult": ParseResult}[name]
    raise AttributeError(name)
