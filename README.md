# turkish-cfg

`turkish-cfg` is planned as a rule-based Turkish constituency parser. The roadmap describes a pipeline that normalizes Turkish text, separates and validates clitics, builds a lattice of possible morphological readings for each token, and lets a Lark Earley CFG parser keep only syntactically valid derivations.

This repository currently contains a skeleton only. The Python modules intentionally document the planned responsibilities and data flow without implementing the parser yet.

## Planned Pipeline

1. `TurkishTokenizer` will normalize input text, split words and punctuation, and expose question clitics such as `mi`, `mı`, `mu`, and `mü` as syntactic tokens after vowel-harmony validation.
2. `MorphologicalAnalyzer` will turn each token into a `TokenNode` containing one or more `MorphState` readings, such as `P1`, `P2`, `P3`, `VP`, or `MI`.
3. `CFGParser` will generate category sequences from the token lattice and parse them with the Lark grammar in `grammar.lark`.
4. `TreeMapper` will reattach the selected surface token, root, and feature dictionary to accepted Lark parse trees.
5. The CLI will print accepted or rejected status, selected lattice readings, discarded alternatives, and a derivation tree.

## Development Status

The first implementation milestone is to replace the explanatory stubs with the smallest working prototype for sentences such as:

```text
Ali kitabı okudu
Kitabı Ali okudu
Ali kitap okudu
```

The parser should accept valid scrambling orders while rejecting cases where a `P2` indefinite object is separated from the verb phrase.

