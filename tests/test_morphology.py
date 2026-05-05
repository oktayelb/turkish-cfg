from __future__ import annotations

from turkish_cfg.morphology import MorphologicalMapper
from turkish_cfg.tokenizer import TurkishTokenizer


def test_tokenizer_does_not_treat_sentence_initial_common_noun_as_proper():
    tokens = TurkishTokenizer().tokenize("Kitap Ali okudu")

    assert tokens[0].normalized == "kitap"
    assert not tokens[0].is_proper
    assert tokens[1].normalized == "ali"
    assert tokens[1].is_proper


def test_mapper_uses_savyar_suffix_names_for_cases_and_verbs():
    mapper = MorphologicalMapper()

    accusative = mapper.map_candidate(
        "kitabı",
        "kitabı",
        False,
        False,
        {
            "root": "kitap",
            "root_pos": "noun",
            "final_pos": "noun",
            "suffixes": [{"name": "accusative_i", "form": "ı", "makes": "NOUN"}],
        },
    )
    verb = mapper.map_candidate(
        "okudu",
        "okudu",
        False,
        False,
        {
            "root": "oku",
            "root_pos": "verb",
            "final_pos": "noun",
            "suffixes": [{"name": "pasttense_di", "form": "du", "makes": "NOUN"}],
        },
    )

    assert accusative.category == "P3"
    assert verb.category == "VP"
