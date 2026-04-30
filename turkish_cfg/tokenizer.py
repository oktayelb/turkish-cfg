"""Tokenization and clitic preprocessing for Turkish text.

This module will contain the first stage of the parser pipeline. Its job is to
convert raw user input into syntactic tokens that later stages can analyze.

Planned responsibilities:
- Normalize Turkish casing carefully. Turkish has dotted and dotless I, so this
  stage should avoid English-centric lowercasing behavior that would corrupt
  forms such as "İstanbul" or "Iğdır".
- Split input on whitespace and sentence punctuation while keeping enough
  source information for good CLI diagnostics.
- Detect yes/no question clitics: "mı", "mi", "mu", and "mü".
- Validate the question clitic against the preceding token using vowel harmony.
- Expose valid clitics as separate syntactic tokens, because the grammar treats
  the question particle as its own terminal category, `MI`.
- Report invalid or orphaned clitics in a structured way instead of silently
  accepting malformed input.

No real tokenization is implemented yet. The class below only defines the
intended API and documents the behavior future implementation should provide.
"""

from __future__ import annotations


class TurkishTokenizer:
    """Normalize text and split it into parser-ready Turkish tokens.

    Future implementation notes:
    - Return a list of token strings in sentence order.
    - Preserve the clitic as its own token after validation.
    - Keep punctuation handling deterministic so parser errors can be explained
      clearly from the CLI.
    - Consider returning a richer token object later if offsets, diagnostics,
      or original casing become important.
    """

    QUESTION_CLITICS = {"mı", "mi", "mu", "mü"}

    def tokenize(self, text: str) -> list[str]:
        """Return normalized syntactic tokens for *text*.

        Planned algorithm:
        1. Normalize whitespace and Turkish-specific casing.
        2. Split punctuation from words without losing meaningful boundaries.
        3. Scan for question clitics.
        4. For each clitic, inspect the previous lexical token's final vowel.
        5. Validate two-way or four-way vowel harmony as needed.
        6. Yield the clitic as a standalone `MI` candidate token for morphology.

        This placeholder deliberately raises `NotImplementedError` so callers do
        not mistake the skeleton for a functioning tokenizer.
        """

        raise NotImplementedError("TurkishTokenizer.tokenize is not implemented yet.")

