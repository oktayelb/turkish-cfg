from __future__ import annotations

from dataclasses import dataclass
import re

_APOSTROPHE_RE = re.compile(r"['’‘]")
# Fixed: Regex now captures the apostrophe and the suffix as a single block
_TOKEN_RE = re.compile(r"[^\W_]+(?:['’‘][^\W_]+)*", re.UNICODE)
_QUESTION_PARTICLES = {"mı", "mi", "mu", "mü"}
_COMMON_PERSON_NAMES = {
    "ali",
    "ayşe",
    "fatma",
    "mehmet",
    "ahmet",
    "mustafa",
    "zeynep",
    "emre",
    "elif",
    "deniz",
}

_TR_LOWER_TABLE = str.maketrans({"I": "ı", "İ": "i"})

def tr_lower(text: str) -> str:
    return text.translate(_TR_LOWER_TABLE).lower()

@dataclass(frozen=True)
class Token:
    surface: str
    normalized: str
    is_proper: bool = False
    is_question_particle: bool = False

class TurkishTokenizer:
    """Small Turkish-aware tokenizer for the CFG pipeline."""

    def tokenize(self, text: str) -> list[Token]:
        tokens: list[Token] = []
        previous_word = ""

        for match in _TOKEN_RE.finditer(text):
            # Now safe to strip the apostrophe since the regex captured it
            surface = _APOSTROPHE_RE.sub("", match.group(0))
            if not surface:
                continue

            normalized = tr_lower(surface)
            is_question = normalized in _QUESTION_PARTICLES
            
            # Improved proper noun detection
            is_proper = surface[:1].isupper() and not is_question

            token = Token(
                surface=surface,
                normalized=normalized,
                is_proper=is_proper,
                is_question_particle=is_question
                and self._matches_question_harmony(previous_word, normalized),
            )
            tokens.append(token)

            if not is_question:
                previous_word = normalized

        return tokens

    def tokenize_words(self, text: str) -> list[str]:
        return [token.normalized for token in self.tokenize(text)]

    def _matches_question_harmony(self, previous_word: str, particle: str) -> bool:
        if not previous_word:
            return True
        last_vowel = next((char for char in reversed(previous_word) if char in "aıoueiöü"), "")
        if not last_vowel:
            return True
        expected = {
            "a": "mı",
            "ı": "mı",
            "o": "mu",
            "u": "mu",
            "e": "mi",
            "i": "mi",
            "ö": "mü",
            "ü": "mü",
        }[last_vowel]
        return particle == expected