# turkish-cfg

`turkish-cfg` is a morphology-aware Turkish CFG parser prototype. The top-level
package tokenizes Turkish text, asks the bundled Savyar analyzer for likely
morphological readings, maps those readings into CFG categories, and parses the
category sequence with Lark.

## How The Project Fits Together

1. `turkish_cfg/tokenizer.py` turns raw Turkish text into normalized tokens.
2. `turkish_cfg/morphology.py` calls Savyar and maps its suffix-level analyses
   into CFG categories such as `P1`, `P3`, `VP`, `MI`, and `GEN`.
3. `turkish_cfg/parser.py` tries the morphological lattice against
   `turkish_cfg/grammar.lark`.
4. `turkish_cfg/tree_mapper.py` renders the accepted derivation back onto the
   original surface words.
5. `turkish_cfg/cli.py` exposes the parser as a command-line tool.

The `savyar/` folder is a bundled Turkish morphological analyzer and ranking
model. It supplies the candidate decompositions used by the CFG parser.

## Root Files

| File | What it does |
| --- | --- |
| `.codex` | Empty local marker file for Codex-related workspace state. |
| `.gitignore` | Ignores Python bytecode caches plus local `.codex` metadata. |
| `README.md` | This file. Explains the repository layout and the purpose of each file. |
| `init.md` | Long research note on Turkish CFG design, morphology, case marking, scrambling, and candidate grammar rules. |
| `pyproject.toml` | Python package metadata, dependency declaration for `lark`, optional `pytest` dependency, and the `turkish-cfg` console script entry point. |
| `roadmap.md` | Implementation roadmap for the Turkish CFG parser, including tokenizer, morphology lattice, parser, tree mapper, and later noun-phrase work. |

## Main Parser Package: `turkish_cfg/`

| File | What it does |
| --- | --- |
| `turkish_cfg/__init__.py` | Package facade that lazily exports `CFGParser` and `ParseResult`. |
| `turkish_cfg/cli.py` | Command-line interface. Parses a sentence, prints accepted/rejected status, selected lattice states, discarded category paths, and the derivation tree. |
| `turkish_cfg/grammar.lark` | Lark grammar over abstract morphology categories. Encodes sentence shapes, scrambling, backgrounded phrases, genitive chains, and the rule that `P2` must be adjacent to `VP`. |
| `turkish_cfg/morphology.py` | Savyar adapter and CFG category mapper. Defines `MorphState`, `TokenNode`, `SavyarInterface`, direct/subprocess Savyar execution, and suffix-to-category logic. |
| `turkish_cfg/parser.py` | CFG parser pipeline. Builds token lattices, enumerates bounded category combinations, parses them with Lark Earley, scores accepted derivations, and reports discarded paths. |
| `turkish_cfg/savyar_worker.py` | JSON-over-stdin subprocess worker used when Savyar must run inside its own virtual environment. |
| `turkish_cfg/tokenizer.py` | Turkish-aware tokenizer. Handles Turkish lowercasing, apostrophes, proper-noun detection, punctuation stripping, and question-particle harmony checks for `mı/mi/mu/mü`. |
| `turkish_cfg/tree_mapper.py` | Renders Lark parse trees as readable ASCII trees and annotates leaves with surface token, selected root, and raw Savyar morphology. |

## Tests And Examples

| File | What it does |
| --- | --- |
| `examples/sample_sentences.txt` | Small list of accepted/rejected sample sentences for parser milestones. |
| `tests/test_morphology.py` | Tests tokenizer proper-noun behavior and `MorphologicalMapper` mappings for accusative nouns and finite verbs. |
| `tests/test_parser.py` | Tests lattice parsing, scrambling acceptance, `P2` adjacency rejection, and CFG-based disambiguation. |

## Savyar Top Level: `savyar/`

| File | What it does |
| --- | --- |
| `savyar/.codex` | Empty local marker file for Codex-related state inside the bundled Savyar tree. |
| `savyar/.gitignore` | Savyar-specific ignore rules for virtualenvs, caches, logs, model checkpoints, generated data, old app code, tools, tests, and samples. |
| `savyar/LICENSE.txt` | License file for the bundled Savyar project. |
| `savyar/README.md` | Turkish-language overview of Savyar's rule-based decomposition plus ML ranking approach and reported training metrics. |
| `savyar/main.py` | Interactive Savyar entry point. Instantiates `AppCLI` and starts the training/evaluation CLI. |
| `savyar/requirements.txt` | Dependency snapshot for the Savyar environment, including PyTorch, NLTK, and supporting packages. |

## Savyar App Layer: `savyar/app/`

| File | What it does |
| --- | --- |
| `savyar/app/cli.py` | Current interactive CLI for Savyar. Displays decompositions, handles word/sentence training choices, evaluation commands, sample processing, stats, and model saves. |
| `savyar/app/data_manager.py` | File I/O layer for dictionaries, logs, metrics, samples, adapted treebanks, validation entries, and persisted training counts. |
| `savyar/app/engine.py` | Main orchestration and ML workflow engine. Contains K-fold utilities, sentence-combination matching, beam-ranked sentence prediction, replay-buffer loading, training, evaluation, and bulk relearning logic. |
| `savyar/app/file_paths.py` | Central list of Savyar data, sample, model, and generated-output paths. |
| `savyar/app/nlp_pipeline.py` | Unified sanitation, morphology reconstruction, suffix-chain encoding, closed-class encoding, and logged-decomposition matching utilities used by the engine and parser integration. |

## Savyar Legacy App Layer: `savyar/app_old/`

This folder is ignored by `savyar/.gitignore` and appears to be a preserved
older split of the current app pipeline.

| File | What it does |
| --- | --- |
| `savyar/app_old/analyzer.py` | Older per-word analyzer that decomposes a word, encodes suffix chains, builds view models, and scores/sorts candidates. |
| `savyar/app_old/cli.py` | Older interactive CLI layer. Similar responsibilities to `savyar/app/cli.py`, but wired to the old module split. |
| `savyar/app_old/data_manager.py` | Older file I/O manager for dictionaries, training logs, metrics, and sample output. |
| `savyar/app_old/file_paths.py` | Older path registry for Savyar data and sample files. |
| `savyar/app_old/input.py` | Older input sanitation helpers for single words and sentences. |
| `savyar/app_old/kfold_cv.py` | Standalone K-fold cross-validation runner and confidence-interval reporter. |
| `savyar/app_old/morphology_adapter.py` | Older suffix-chain encoder, morphology reconstructor, and logged-entry matcher. |
| `savyar/app_old/sequence_matcher.py` | Older DFS/beam utilities for matching user-entered sentence decomposition prefixes and ranking combinations. |
| `savyar/app_old/workflows.py` | Older workflow engine connecting CLI, analyzer, data manager, trainer, and bulk training flows. |

## Savyar ML Layer: `savyar/ml/`

| File | What it does |
| --- | --- |
| `savyar/ml/config.py` | Dataclass configuration for model paths, Transformer dimensions, optimizer settings, ranking objective, curriculum settings, batch sizes, validation split, and replay buffer behavior. |
| `savyar/ml/ml_ranking_model.py` | PyTorch Transformer model and trainer. Encodes suffix/closed-class sequences, scores complete candidate analyses, trains ranking and masked-token objectives, handles checkpointing, and provides scoring helpers. |
| `savyar/ml/model.pt` | Local trained model checkpoint used by Savyar's `Trainer`. It is a generated/local artifact and is ignored by `savyar/.gitignore`. |

## Savyar Morphology Core: `savyar/util/`

| File | What it does |
| --- | --- |
| `savyar/util/README.md` | Detailed documentation of the rule-based decomposer, suffix hierarchy, suffix folders, closed-class words, dictionary utilities, and decomposition algorithm. |
| `savyar/util/decomposer.py` | Rule-based morphological analyzer. Enumerates roots, handles reduplication, searches suffix chains with Turkish ordering constraints, integrates closed-class words, and exposes `decompose()` / `decompose_with_cc()`. |
| `savyar/util/suffix.py` | Base suffix model. Defines `SuffixGroup`, `Type`, and `Suffix`, including vowel harmony, consonant hardening, vowel-collision handling, and softened suffix variants. |
| `savyar/util/word_methods.py` | Dictionary and phonology utilities. Loads noun/verb dictionaries, implements Turkish lowercasing, vowel harmony, root mutation recovery, derived-word detection, random word selection, and dictionary deletion helpers. |

## Savyar Suffix Files: `savyar/util/suffixes/`

| File | What it does |
| --- | --- |
| `savyar/util/suffixes/n2n_suffixes.py` | Aggregates noun-to-noun suffix groups into `NOUN2NOUN`. |
| `savyar/util/suffixes/n2v_suffixes.py` | Aggregates noun-to-verb suffixes into `NOUN2VERB`. |
| `savyar/util/suffixes/v2n_suffixes.py` | Aggregates verb-to-noun suffix groups into `VERB2NOUN`. |
| `savyar/util/suffixes/v2v_suffixes.py` | Aggregates verb-to-verb suffix groups into `VERB2VERB`. |
| `savyar/util/suffixes/suffix_info.md` | Generated/reference lookup for suffix identifiers, groups, transition rules, and implementation notes. |

### Noun To Noun Suffixes: `savyar/util/suffixes/n2n/`

| File | What it does |
| --- | --- |
| `savyar/util/suffixes/n2n/adverbials.py` | Defines noun/adjective-to-adverb style suffixes such as `temporative_leyin`, `adverbial_in`, `adverbial_cesine`, and `when_ken`. |
| `savyar/util/suffixes/n2n/case_suffixes.py` | Defines Turkish case suffix behavior for genitive (`noun_compound`), accusative, dative, locative, and ablative, including possessive-context buffer rules. |
| `savyar/util/suffixes/n2n/conjugation_suffixes.py` | Defines person/agreement suffixes that can attach after nominalized or predicative forms. |
| `savyar/util/suffixes/n2n/copula.py` | Defines nominal predicative/copula suffixes such as `-dir`, past copula, conditional, and evidential copula. |
| `savyar/util/suffixes/n2n/derivationals.py` | Defines noun-to-noun derivational suffixes such as actor, privative, compositive, suitability, diminutive, ordinal, relative, and family/group markers. |
| `savyar/util/suffixes/n2n/intensifier.py` | Placeholder for intensifier/reduplication support; the active reduplication logic is handled in `decomposer.py`. |
| `savyar/util/suffixes/n2n/marking_suffix.py` | Defines the post-case `-ki` marker and its context-sensitive form rules. |
| `savyar/util/suffixes/n2n/plural_suffix.py` | Defines the plural suffix `plural_ler`. |
| `savyar/util/suffixes/n2n/possessive_suffix.py` | Defines possessive agreement suffixes for first/second/third person singular and plural. |
| `savyar/util/suffixes/n2n/with_le.py` | Defines the comitative/instrumental `-le/-la` suffix (`confactuous_le`). |

### Noun To Verb Suffixes: `savyar/util/suffixes/n2v/`

| File | What it does |
| --- | --- |
| `savyar/util/suffixes/n2v/verbifiers.py` | Defines noun-to-verb derivational suffixes such as `-le` and `-se`. |

### Verb To Noun Suffixes: `savyar/util/suffixes/v2n/`

| File | What it does |
| --- | --- |
| `savyar/util/suffixes/v2n/gerunds.py` | Defines verbal adverb/gerund suffixes such as `-erek`, `-ince`, `-ip`, optative/adverbial `-e`, `-eli`, and `-meksizin`. |
| `savyar/util/suffixes/v2n/infinitives.py` | Defines infinitive/verbal-noun suffixes such as `infinitive_me` and `infinitive_mek`. |
| `savyar/util/suffixes/v2n/nounifiers.py` | Defines verb-to-noun derivational suffixes such as `-ek`, `-gen`, `-ik`, `-gi`, `-im`, `-inti`, `-anak`, and related nounifiers. |
| `savyar/util/suffixes/v2n/participles.py` | Defines participial and nominalizing suffixes such as `factative_en`, `adjectifier_dik`, `nounifier_ecek`, aorist, and desiderative forms. |
| `savyar/util/suffixes/v2n/predicatives.py` | Defines tense/predicative verb-to-noun suffixes such as past tense and wish/conditional forms. |

### Verb To Verb Suffixes: `savyar/util/suffixes/v2v/`

| File | What it does |
| --- | --- |
| `savyar/util/suffixes/v2v/verb_compounds.py` | Defines compound/auxiliary verb suffixes such as continuous `-iyor`, ability, near-action, continuative, persistive, and suddenative forms. |
| `savyar/util/suffixes/v2v/verb_derivationals.py` | Defines verb voice/derivation suffixes such as reciprocal, causative, passive, reflexive, and related forms. |
| `savyar/util/suffixes/v2v/verb_negative.py` | Defines negation and inability suffixes (`negative_me`, `negative_able`). |

## Savyar Closed-Class Words: `savyar/util/words/`

| File | What it does |
| --- | --- |
| `savyar/util/words/__init__.py` | Re-exports word and closed-class classes/lookups for convenient imports. |
| `savyar/util/words/closed_class.py` | Defines fixed grammatical word classes: pronouns, conjunctions, postpositions, adverbs, determiners, interjections, particles, closed-class lookup tables, and marker wrappers. |
| `savyar/util/words/numerals.py` | Defines numeral lexemes and integer-to-Turkish-word expansion used by closed-class/numeral handling. |
| `savyar/util/words/words.py` | Base `Word` class for applying suffix objects to a surface word and tracking POS changes. |

## Savyar Data: `savyar/data/`

| File | What it does |
| --- | --- |
| `savyar/data/ekistemez.txt` | Small list of forms that should not accept suffixes or should be excluded from ordinary suffixing behavior. |
| `savyar/data/eşkelam.txt` | Auxiliary word-pair list used by Savyar data/dictionary work. |
| `savyar/data/final_suffix_metrics.json` | Saved training/validation metrics for rank accuracy, top-k accuracy, suffix precision/recall/F1, and per-suffix/group metrics. |
| `savyar/data/mastarad.txt` | Small list of infinitive-like or root forms used as special dictionary/morphology data. |
| `savyar/data/sentence_valid_decompositions.jsonl` | Confirmed sentence-level decomposition log used for replay/bulk training. |
| `savyar/data/training_count.txt` | Persisted count of Savyar training examples/updates. |
| `savyar/data/treebank_vnoun.py` | Shared helper for treebank adapters to resolve ambiguous verbal-noun suffixes from surface forms. |
| `savyar/data/verbs.txt` | Dictionary of Turkish verb roots. |
| `savyar/data/verbs_transitivity.txt` | Verb transitivity annotations for dictionary/reference use. |
| `savyar/data/word_decompositions.jsonl` | Confirmed or generated word-level decompositions used by Savyar training/debugging flows. |
| `savyar/data/words.txt` | Main open-class word dictionary loaded by `word_methods.py`. |

### BOUN Treebank: `savyar/data/boun_treebank/`

| File | What it does |
| --- | --- |
| `savyar/data/boun_treebank/tr_boun-ud-dev.conllu` | BOUN Turkish Universal Dependencies development split. |
| `savyar/data/boun_treebank/tr_boun-ud-test.conllu` | BOUN Turkish Universal Dependencies test split. |
| `savyar/data/boun_treebank/tr_boun-ud-train.conllu` | BOUN Turkish Universal Dependencies training split. |
| `savyar/data/boun_treebank/treebank_adapter.py` | Converts BOUN UD features into Savyar suffix-name JSONL, validating against the decomposer where possible. |
| `savyar/data/boun_treebank/treebank_adaptation_stats.json` | Generated statistics from the BOUN adapter run. |
| `savyar/data/boun_treebank/treebank_adapted.jsonl` | Generated BOUN training entries in Savyar decomposition format. |
| `savyar/data/boun_treebank/treebank_adapted_sentence_diagnostics.jsonl` | Generated per-sentence diagnostics from BOUN adaptation. |
| `savyar/data/boun_treebank/treebank_adapted_unmatched.jsonl` | Generated BOUN entries that could not be confidently matched. |
| `savyar/data/boun_treebank/unmapped_features.json` | Generated report of BOUN feature values not yet mapped to Savyar suffixes. |

### Google Treebank: `savyar/data/google_treebank/`

| File | What it does |
| --- | --- |
| `savyar/data/google_treebank/web.conllu` | Google Turkish UD web-domain treebank source. |
| `savyar/data/google_treebank/wiki.conllu` | Google Turkish UD Wikipedia-domain treebank source. |
| `savyar/data/google_treebank/treebank_adapter.py` | Converts Google UD inflection-group features into Savyar suffix-name JSONL. |
| `savyar/data/google_treebank/treebank_adaptation_stats.json` | Generated statistics from the Google adapter run. |
| `savyar/data/google_treebank/treebank_adapted.jsonl` | Generated Google treebank training entries in Savyar format. |
| `savyar/data/google_treebank/treebank_adapted_sentence_diagnostics.jsonl` | Generated per-sentence diagnostics from Google adaptation. |
| `savyar/data/google_treebank/treebank_adapted_unmatched.jsonl` | Generated Google entries that could not be confidently matched. |
| `savyar/data/google_treebank/unmapped_features.json` | Generated report of Google feature values not yet mapped to Savyar suffixes. |

### GPT/Text Treebank: `savyar/data/gpt_treebank/`

| File | What it does |
| --- | --- |
| `savyar/data/gpt_treebank/islenmis_cumleler.txt` | Sentence-split text output produced from the source novel text. |
| `savyar/data/gpt_treebank/kurk_mantolu_madonna.jsonl` | Hand/GPT-style sentence decomposition entries in Savyar JSONL format. |
| `savyar/data/gpt_treebank/kurk_mantolu_madonna.txt` | Source text used for sentence extraction. |
| `savyar/data/gpt_treebank/metin_isleyici.py` | NLTK-based Turkish sentence splitter and text cleaner for the source text. |

### METU Treebank: `savyar/data/metu_treebank/`

| File | What it does |
| --- | --- |
| `savyar/data/metu_treebank/METUSABANCI_treebank_v-1.conll` | METU-Sabanci Turkish treebank source file. |
| `savyar/data/metu_treebank/treebank_adapter.py` | Converts METU-Sabanci morphological feature strings into Savyar suffix-name JSONL. |
| `savyar/data/metu_treebank/treebank_adaptation_stats.json` | Generated statistics from the METU adapter run. |
| `savyar/data/metu_treebank/treebank_adapted.jsonl` | Generated METU training entries in Savyar format. |
| `savyar/data/metu_treebank/treebank_adapted_sentence_diagnostics.jsonl` | Generated per-sentence diagnostics from METU adaptation. |
| `savyar/data/metu_treebank/treebank_adapted_unmatched.jsonl` | Generated METU entries that could not be confidently matched. |

## Savyar Documentation: `savyar/docs/`

| File | What it does |
| --- | --- |
| `savyar/docs/decomposer.md` | Explains Savyar's root enumeration, recursive suffix-chain search, transition table, and waterfall suffix ordering. |
| `savyar/docs/ml_model.md` | Documents the Transformer ranking model, candidate encoding, training objective, and bulk relearning approach. |
| `savyar/docs/workflows.md` | Documents Savyar workflow orchestration for word analysis, sentence analysis, training commits, and relearning. |

## Savyar Logs: `savyar/logs/`

These are generated diagnostic artifacts.

| File | What it does |
| --- | --- |
| `savyar/logs/failed_adapter_sentences_report.json` | Grouped analysis of treebank adapter sentence failures. |
| `savyar/logs/match_failed.jsonl` | Logged cases where stored decompositions no longer match current decomposer output. |
| `savyar/logs/no_decomp.jsonl` | Logged words or entries for which no decomposition was found. |
| `savyar/logs/unmapped_treebank_report.json` | Summary report of unmapped treebank features/items. |

## Savyar Sample Files: `savyar/sample/`

| File | What it does |
| --- | --- |
| `savyar/sample/sample.txt` | Sample word list used by Savyar's sample-analysis flow. |
| `savyar/sample/sample_decomposed.txt` | Output of word-by-word sample decomposition. |
| `savyar/sample/sample_sentence.txt` | Sample sentence input used by Savyar's sentence-analysis flow. |
| `savyar/sample/sample_sentence_decomposed.txt` | Output of sample sentence decomposition. |

## Savyar Tooling: `savyar/tools/`

| File | What it does |
| --- | --- |
| `savyar/tools/analyze_failed_adapter_sentences.py` | Groups failed treebank-adapter sentences into fixable categories and can emit a JSON report. |
| `savyar/tools/dict_script.py` | Interactive dictionary cleanup helper for removing forms that share one root but end in an unwanted suffix. |
| `savyar/tools/explain_token_id.py` | Explains model token IDs as special tokens, suffix names, or closed-class entries. |
| `savyar/tools/inspect_suffix_failures.py` | Inspects model false positives/false negatives for selected suffixes across adapted datasets. |
| `savyar/tools/show_unmapped_treebank_items.py` | Reads unmatched adapter logs and prints grouped unmapped feature examples. |

## Savyar Tests: `savyar/tests/`

| File | What it does |
| --- | --- |
| `savyar/tests/__init__.py` | Marks the Savyar test directory as a Python package. |
| `savyar/tests/test_ablative_den.py` | Tests ablative suffix surface forms, decomposition paths, and legacy `meden` encoding compatibility. |
| `savyar/tests/test_case_suffix_buffers.py` | Tests case-buffer consonants, invalid doubled-vowel forms, `-ki`, conjugation contexts, and `-iyor` form behavior. |
| `savyar/tests/test_word_methods_dictionary.py` | Tests infinitive generation, dictionary deletion, and persistence of word/verb dictionary edits. |

## Generated Or Local Directories

| Directory | What it does |
| --- | --- |
| `.git/` | Git repository metadata. Do not edit directly. |
| `.pytest_cache/` | Local cache produced by pytest. Safe to delete. |
| `*/__pycache__/` | Python bytecode caches. Safe to delete. |
| `savyar/.venv/` | Local Savyar virtual environment. It is used when `SavyarInterface` falls back to subprocess execution. |
