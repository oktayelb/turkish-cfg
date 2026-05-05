# Comprehensive Roadmap: Rule-Based Turkish CFG Parser

## Goal

Build a rule-based Turkish CFG parser capable of handling agglutinative morphology, free constituent order (scrambling), and morphological ambiguity. The system will ingest a sentence, process it through Savyar to get a highly accurate token lattice, apply a recursive CFG via the Earley algorithm, and output valid syntactic derivation trees while filtering out grammatically impossible morphological interpretations.

---

## Phase 1: Scope & Architectural Core

**Initial Subset Target:**

* Simple declarative and interrogative sentences.
* Scrambling handling (SOV, OSV, OVS, SVO).
* Case-marked noun phrases (P1 through P9).
* Optional dropped subjects (pro-drop).
* Separation and validation of clitics (e.g., *mi*).

**The Architectural Pivot:**
The parser will not use a 1:1 token-to-terminal mapping. Because Turkish morphology is highly ambiguous, the morphological analyzer must output a Token Lattice (a list of all possible states for each word). By integrating Savyar, this lattice will be restricted to Savyar's top 3 predictions (yielding ~99% accuracy) rather than generating an exhaustive list of mathematically possible but improbable permutations. The CFG parser acts as the disambiguation engine, attempting to build a tree with every path in the top-3 lattice and keeping only the mathematically valid derivations.

---

## Phase 2: Formal Grammar Layer (The Lark CFG)

Instead of hardcoding permutations (which causes a factorial explosion), the grammar will utilize a recursive `pre_verbal` container. We will use the Lark parsing library's EBNF syntax.

**Draft `grammar.lark` definition:**

```ebnf
start: sentence

// A sentence is a sequence of pre-verbal phrases followed by a verb, optionally followed by a question clitic.
sentence: pre_verbal vp question_particle?
        | vp background_phrase?       // Handles inverted (devrik) sentences
        | pre_verbal                  // Handles incomplete (eksiltili) sentences

// The Pre-Verbal block recursively collects any phrase.
// The P2 constraint is enforced here: P2 can ONLY appear immediately before the VP.
pre_verbal: phrase* p2 
          | phrase*

// Phrasal mappings (tied directly to morphological case tags)
phrase: p1 | p3 | p4 | p5 | p6 | p7 | p8 | p9

// Terminals (These will be dynamically injected from the mapped Savyar output)
p1: "P1"  // Nominative (Subject / Possessive)
p2: "P2"  // Nominative (Indefinite Object)
p3: "P3"  // Accusative
p4: "P4"  // Dative
vp: "VP"  // Verb Phrase
question_particle: "MI"
```

---

## Phase 3: Tokenization & Clitic Pre-Processing

Turkish whitespace does not neatly align with syntactic boundaries. Clitics like *mi* are written separately but depend on the preceding word's vowels.

**Code Structure (`tokenizer.py`):**

```python
class TurkishTokenizer:
    def tokenize(self, text: str) -> list[str]:
        # 1. Lowercase and handle Turkish specific characters (I/ı, İ/i)
        # 2. Split by whitespace and punctuation
        # 3. Identify clitics (mı, mi, mu, mü) and temporarily attach them 
        #    to the previous token for vowel harmony validation, then yield them 
        #    as separate syntactic tokens.
        pass
```

---

## Phase 4: Savyar Integration & Token Lattice

This is the critical data structure. The morphological analyzer wraps the Savyar model to return a focused lattice of possibilities. Savyar provides top-tier decomposition predictions (noun compound, case, pronoun, possessive, conjugation). The team must map Savyar's custom outputs to the CFG terminals.

**Code Structure (`morphology.py`):**

```python
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class MorphState:
    category: str              # CFG terminal (e.g., 'P3', 'VP')
    root: str                  # Root word (e.g., 'kitap')
    features: Dict[str, str]   # e.g., {'raw_savyar': 'kitap+accusative_i', 'case': 'acc'}

@dataclass
class TokenNode:
    surface: str               # Original text (e.g., 'kitabı')
    states: List[MorphState]   # Savyar top-3 predictions mapped

class MorphologicalAnalyzer:
    def __init__(self):
        # Initialize Savyar environment and model
        pass

    def analyze(self, token: str) -> TokenNode:
        """
        Query Savyar for the token.
        Take top-3 predictions (~99% accuracy).
        Map suffix strings to MorphState.
        """
        pass
```

---

## Phase 5: Parser Pipeline Implementation

The parser converts the TokenNode lattice into a stream of strings for Lark, then maps the resulting parse tree back to morphological data.

**Code Structure (`parser.py`):**

```python
from lark import Lark
from morphology import TokenNode

class CFGParser:
    def __init__(self, grammar_file: str):
        with open(grammar_file, 'r') as f:
            self.parser = Lark(f.read(), start='start', parser='earley', ambiguity='explicit')
            
    def parse_lattice(self, nodes: list[TokenNode]):
        # 1. Generate linear combinations from Savyar top-3 lattice
        # 2. Feed combinations into Lark
        # 3. Keep valid trees, discard invalid ones
        pass
```

---

## Phase 6: Noun Phrase Internals & İzafet (Later Phases)

Once sentence-level parsing stabilizes, expand grammar for nested phrases.

**Updated grammar snippet:**

```ebnf
p1: x
p3: x acc_suffix
p4: x dat_suffix

x: noun
 | adj x
 | det x
 | x noun
 | x gen_suffix x pos_suffix
```

---

## Phase 7: Project & File Structure

```plaintext
turkish_cfg/
├── pyproject.toml
├── README.md
├── turkish_cfg/
│   ├── __init__.py
│   ├── tokenizer.py
│   ├── morphology.py
│   ├── grammar.lark
│   ├── parser.py
│   ├── tree_mapper.py
│   └── cli.py
├── tests/
│   ├── test_morphology.py
│   ├── test_scrambling.py
│   ├── test_constraints.py
│   └── test_izafet.py
└── examples/
    └── sample_sentences.txt
```

---

## Phase 8: Testing Strategy & Milestones

**Test Requirements:**
Each test must verify acceptance/rejection and correct morphological disambiguation.

**Examples:**

* `test_valid_scrambling`:
  "Ali kitabı okudu" → Accept
  "Kitabı Ali okudu" → Accept

* `test_p2_constraint`:
  "Ali kitap okudu" → Accept
  "Kitap Ali okudu" → Reject

* `test_disambiguation`:
  "Kitabı okudu" → Accept P3, reject P1 alternative

---

## Phase 9: Expected First Prototype Output

**Command:**

```bash
python -m turkish_cfg.cli "Ali kitabı okudu"
```

**Terminal Output:**

```plaintext
STATUS: ACCEPTED (1 valid derivation found)

--- LATTICE RESOLUTION ---
Ali    -> Selected: P1 (Root: Ali, Case: Nom)
kitabı -> Selected: P3 (Root: kitap, Raw: kitap+accusative_i)
okudu  -> Selected: VP (Root: oku, Tense: Past, Person: 3SG)

--- DERIVATION TREE ---
Start
└── Sentence
    ├── PreVerbal
    │   ├── Phrase (P1)
    │   │   └── Ali
    │   └── Phrase (P3)
    │       └── kitabı (kitap+accusative_i)
    └── VP
        └── okudu (oku+past_du)
```
