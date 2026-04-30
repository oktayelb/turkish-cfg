# Comprehensive Roadmap: Rule-Based Turkish CFG Parser

## Goal
Build a rule-based Turkish CFG parser capable of handling agglutinative morphology, free constituent order (scrambling), and morphological ambiguity. The system will ingest a sentence, process it through a token lattice, apply a recursive CFG via the Earley algorithm, and output valid syntactic derivation trees while filtering out grammatically impossible morphological interpretations.

---

## Phase 1: Scope & Architectural Core

**Initial Subset Target:**
*   Simple declarative and interrogative sentences.
*   Scrambling handling (SOV, OSV, OVS, SVO).
*   Case-marked noun phrases (P1 through P9).
*   Optional dropped subjects (pro-drop).
*   Separation and validation of clitics (e.g., *mi*).

**The Architectural Pivot:**
The parser will **not** use a 1:1 token-to-terminal mapping. Because Turkish morphology is highly ambiguous (e.g., *kitabı* can be Nominative+Possessive or Accusative), the morphological analyzer must output a **Token Lattice** (a list of all possible states for each word). The CFG parser acts as the disambiguation engine, attempting to build a tree with every path and keeping only the mathematically valid derivations.

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

// Terminals (These will be dynamically injected from the morphological lattice)
p1: "P1"  // Nominative (Subject / Possessive)
p2: "P2"  // Nominative (Indefinite Object)
p3: "P3"  // Accusative
p4: "P4"  // Dative
vp: "VP"  // Verb Phrase
question_particle: "MI"

Phase 3: Tokenization & Clitic Pre-Processing

Turkish whitespace does not neatly align with syntactic boundaries. Clitics like mi are written separately but depend on the preceding word's vowels.

Code Structure (tokenizer.py):
Python

class TurkishTokenizer:
    def tokenize(self, text: str) -> List[str]:
        # 1. Lowercase and handle Turkish specific characters (I/ı, İ/i)
        # 2. Split by whitespace and punctuation
        # 3. Identify clitics (mı, mi, mu, mü) and temporarily attach them 
        #    to the previous token for vowel harmony validation, then yield them 
        #    as separate syntactic tokens.
        pass

Phase 4: Morphological Analysis & The Token Lattice

This is the critical data structure. The morphological analyzer must return a lattice of possibilities for each token.

Code Structure (morphology.py):
Python

from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class MorphState:
    category: str              # The CFG terminal it maps to (e.g., 'P3', 'VP')
    root: str                  # The root word (e.g., 'kitap')
    features: Dict[str, str]   # e.g., {'case': 'acc', 'number': 'sg'}

@dataclass
class TokenNode:
    surface: str               # The original text (e.g., 'kitabı')
    states: List[MorphState]   # All possible morphological interpretations

class MorphologicalAnalyzer:
    def analyze(self, token: str) -> TokenNode:
        """
        Example for token = "kitabı"
        Returns:
        TokenNode(surface="kitabı", states=[
            MorphState(category="P3", root="kitap", features={"case": "acc"}),
            MorphState(category="P1", root="kitap", features={"case": "nom", "possessive": "3sg"}),
            MorphState(category="P2", root="kitap", features={"case": "nom", "possessive": "3sg"})
        ])
        """
        pass

Phase 5: Parser Pipeline Implementation

The parser must convert the TokenNode lattice into a stream of strings that Lark can parse, and then map the resulting Lark tree back to the rich morphological data.

Code Structure (parser.py):
Python

from lark import Lark
from morphology import MorphologicalAnalyzer, TokenNode

class CFGParser:
    def __init__(self, grammar_file: str):
        with open(grammar_file, 'r') as f:
            # We use Earley to handle the heavy ambiguity of the lattice
            self.parser = Lark(f.read(), start='start', parser='earley', ambiguity='explicit')
            
    def parse_lattice(self, nodes: List[TokenNode]):
        # 1. Generate all possible linear combinations of categories from the lattice.
        #    If Ali (1 state) kitabı (3 states) okudu (1 state) -> 3 permutations.
        #    ['P1', 'P3', 'VP'], ['P1', 'P1', 'VP'], ['P1', 'P2', 'VP']
        
        # 2. Feed each combination into the Lark parser.
        
        # 3. Collect valid trees. Discard combinations that throw lark.exceptions.UnexpectedToken.
        pass

Phase 6: Noun Phrase Internals & İzafet (Later Phases)

Once the sentence-level scrambling works, expand the grammar to handle nested phrases.

Updating grammar.lark for Nouns (X):
EBNF

// A generic Noun Phrase (X) takes a case suffix to become a P-phrase
p1: x
p3: x acc_suffix
p4: x dat_suffix

// Internal structure of X
x: noun
 | adj x                  // Modifier
 | det x                  // Determiner
 | x noun                 // Bare compound (deniz otobüsü)
 | x gen_suffix x pos_suffix // İzafet recursion (okulun kapısı)

Phase 7: Project & File Structure
Plaintext

turkish_cfg/
├── pyproject.toml
├── README.md
├── turkish_cfg/
│   ├── __init__.py
│   ├── tokenizer.py        # Normalizes text, extracts and validates clitics.
│   ├── morphology.py       # Houses the MorphologicalAnalyzer, TokenNode, and MorphState classes.
│   ├── grammar.lark        # The actual text file containing the EBNF grammar rules.
│   ├── parser.py           # Wraps Lark, generates lattice permutations, and executes the parse.
│   ├── tree_mapper.py      # Takes the raw Lark tree and re-attaches the 'root' and 'features' dicts to the nodes.
│   └── cli.py              # Command-line interface logic (argparse).
├── tests/
│   ├── test_morphology.py  # Tests that ambiguous words return multiple correct states.
│   ├── test_scrambling.py  # Tests SOV, OSV, OVS, etc.
│   ├── test_constraints.py # Tests that P2 strictly precedes the VP.
│   └── test_izafet.py      # Tests recursive genitive-possessive chains.
└── examples/
    └── sample_sentences.txt

Phase 8: Testing Strategy & Milestones

Test Suite Requirements:
Every test must assert whether the parser accepts or rejects the sentence, and if accepted, whether the correct morphological state was chosen from the lattice.

Examples:

    test_valid_scrambling: "Ali kitabı okudu" (Accept), "Kitabı Ali okudu" (Accept).

    test_p2_constraint: "Ali kitap okudu" (Accept), "Kitap Ali okudu" (Reject - P2 must touch VP).

    test_disambiguation: "Kitabı okudu" (Accepts P3, rejects P1 because 'okudu' needs a subject or object, and an object makes more syntactic sense here, or accepts pro-drop subject + P3 object).

Phase 9: Expected First Prototype Output

Command:
python -m turkish_cfg.cli "Ali kitabı okudu"

Terminal Output:
Plaintext

STATUS: ACCEPTED (1 valid derivation found)

--- LATTICE RESOLUTION ---
Ali    -> Selected: P1 (Root: Ali, Case: Nom)
kitabı -> Selected: P3 (Root: kitap, Case: Acc) [Discarded: P1, P2]
okudu  -> Selected: VP (Root: oku, Tense: Past, Person: 3SG)

--- DERIVATION TREE ---
Start
└── Sentence
    ├── PreVerbal
    │   ├── Phrase (P1)
    │   │   └── Ali
    │   └── Phrase (P3)
    │       └── kitabı (kitap + ı)
    └── VP
        └── okudu (oku + du)
