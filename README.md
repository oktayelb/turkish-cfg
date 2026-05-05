# turkish-cfg

`turkish-cfg` is planned as a rule-based Turkish constituency parser. The roadmap describes a pipeline that normalizes Turkish text, utilizes a dedicated morphological prediction model, builds a focused lattice of possible morphological readings for each token, and lets a Lark Earley CFG parser keep only syntactically valid derivations.[cite: 1]

## Savyar Integration

We have added Savyar into the codebase to handle all morphological predictions. Using this tool will significantly streamline development for the CFG parser.

*   **Environment:** Savyar has its own virtual environment (venv) and is ready to run.
*   **Model Accuracy:** It features a predictive model that outputs the correct morphological decomposition of a Turkish sentence with an 86% top-1 accuracy. More importantly, the probability of the correct sentence being in the top 3 guesses is 99%. We will use these top 3 guesses to heavily optimize our parser's search space.
*   **Output Data:** Savyar provides detailed decomposition, giving you noun compound, case, pronoun, possessive, and conjugation information. Its outputs are formatted like the examples found in its `.jsonl` files.
*   **Suffix Conventions:** Savyar uses a custom naming convention for its outputs (e.g., outputting `base_word+suffix_tag` rather than standard linguistic tags). You must review `savyar/util/suffixes/suffix_info.md` to understand the codebase's specific suffix tags.

## Planned Pipeline

1. `TurkishTokenizer` will normalize input text, split words and punctuation, and expose question clitics such as `mi`, `mı`, `mu`, and `mü` as syntactic tokens after vowel-harmony validation.[cite: 1]
2. `SavyarInterface` will process the tokens and return the top 3 morphological predictions to capture the 99% accuracy threshold.
3. `MorphologicalMapper` will translate Savyar's custom outputs (e.g., `+accusative_i`) into our CFG's internal `MorphState` readings (such as `P1`, `P2`, `P3`, `VP`, or `MI`).[cite: 1]
4. `CFGParser` will generate category sequences from the Savyar-pruned token lattice and parse them with the Lark grammar in `grammar.lark`.[cite: 1]
5. `TreeMapper` will reattach the selected surface token, root, and feature dictionary to accepted Lark parse trees.[cite: 1]
6. The CLI will print accepted or rejected status, selected lattice readings, discarded alternatives, and a derivation tree.[cite: 1]

## Development Status

The first implementation milestone is to replace the explanatory stubs with the smallest working prototype for sentences such as:[cite: 1]

```text
Ali kitabı okudu
Kitabı Ali okudu
Ali kitap okudu

The parser should accept valid scrambling orders while rejecting cases where a P2 indefinite object is separated from the verb phrase.