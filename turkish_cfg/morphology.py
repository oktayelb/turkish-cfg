from __future__ import annotations

from dataclasses import dataclass, field
import importlib
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable

from .tokenizer import Token

@dataclass(frozen=True)
class MorphState:
    category: str
    root: str
    features: dict[str, Any] = field(default_factory=dict)
    rank: int = 0
    score: float = 0.0

@dataclass(frozen=True)
class TokenNode:
    surface: str
    normalized: str
    states: list[MorphState]

class SavyarUnavailable(RuntimeError):
    pass

class SavyarInterface:
    """Adapter around Savyar's sentence ranker.

    Savyar owns the heavy morphology and ML work. This class asks it for the
    top sentence decompositions, then converts the selected decomposition for
    each token into CFG-facing `MorphState` objects.
    """

    def __init__(
        self,
        savyar_dir: str | Path | None = None,
        top_k: int = 3,
        prefer_subprocess: bool = False,
    ) -> None:
        self.savyar_dir = Path(savyar_dir or Path(__file__).resolve().parents[1] / "savyar")
        self.top_k = top_k
        self.mapper = MorphologicalMapper()
        self._direct: _DirectSavyar | None = None
        self._prefer_subprocess = prefer_subprocess

        if not prefer_subprocess:
            try:
                self._direct = _DirectSavyar(self.savyar_dir)
            except Exception:
                self._direct = None

    def analyze(self, tokens: Iterable[Token]) -> list[TokenNode]:
        token_list = list(tokens)
        if not token_list:
            return []

        if self._direct is not None:
            payload = self._direct.analyze(token_list, self.top_k)
        else:
            payload = self._analyze_subprocess(token_list)

        nodes: list[TokenNode] = []
        for token_payload in payload["tokens"]:
            states = [
                self.mapper.map_candidate(
                    token_payload["surface"],
                    token_payload["normalized"],
                    bool(token_payload.get("is_proper")),
                    bool(token_payload.get("is_question_particle")),
                    candidate,
                )
                for candidate in token_payload.get("candidates", [])
            ]
            nodes.append(
                TokenNode(
                    surface=token_payload["surface"],
                    normalized=token_payload["normalized"],
                    states=self.mapper.deduplicate_states(states),
                )
            )
        return nodes

    def _analyze_subprocess(self, tokens: list[Token]) -> dict[str, Any]:
        python = self.savyar_dir / ".venv" / "bin" / "python"
        if not python.exists():
            raise SavyarUnavailable(f"Savyar venv not found at {python}")

        request = {
            "savyar_dir": str(self.savyar_dir),
            "top_k": self.top_k,
            "tokens": [token.__dict__ for token in tokens],
        }
        proc = subprocess.run(
            [str(python), "-m", "turkish_cfg.savyar_worker"],
            cwd=str(Path(__file__).resolve().parents[1]),
            input=json.dumps(request, ensure_ascii=False),
            text=True,
            capture_output=True,
            check=False,
        )
        if proc.returncode != 0:
            raise SavyarUnavailable(proc.stderr.strip() or "Savyar subprocess failed")
        return json.loads(proc.stdout)

class MorphologicalMapper:
    # Fixed syntactic case assignments to align with linguistic norms
    CASE_TO_CATEGORY = {
        "accusative_i": "P3",
        "dative_e": "P4",
        "locative_de": "P5",
        "ablative_den": "P6",
        "confactuous_le": "P7",
        "noun_compound": "GEN",
    }
    PRONOUN_CASES = {
        "ben": "P1",
        "sen": "P1",
        "o": "P1",
        "biz": "P1",
        "siz": "P1",
        "onlar": "P1",
        "beni": "P3",
        "seni": "P3",
        "onu": "P3",
        "bizi": "P3",
        "sizi": "P3",
        "bana": "P4",
        "sana": "P4",
        "ona": "P4",
        "bize": "P4",
        "size": "P4",
    }
    ADVERBIAL_SUFFIXES = {
        "temporative_leyin",
        "adverbial_cesine",
        "when_ken",
        "adverbial_erek",
        "adverbial_ince",
        "adverbial_ip",
        "adverbial_e",
        "adverbial_dikçe",
        "since_eli",
        "undoing_meksizin",
    }
    FINITE_VERB_SUFFIXES = {
        "pasttense_di",
        "continuous_iyor",
        "wish_suffix",
        "pasttense_noundi",
        "copula_mis",
        "nounaorist_dir",
        "if_se",
        "conjugation_1sg",
        "conjugation_2sg",
        "conjugation_3sg",
        "conjugation_1pl",
        "conjugation_2pl",
        "conjugation_3pl",
    }
    NONFINITE_VERB_TO_NOUN = {
        "factative_en",
        "pastfactative_miş",
        "adjectifier_dik",
        "nounifier_ecek",
        "factative_ir",
        "willing_esi",
        "infinitive_me",
        "infinitive_mek",
        "nounifier_iş",
        "toolative_ek",
        "constofactative_gen",
        "constofactative_gin",
        "perfectative_ik",
        "nounifier_i",
        "nounifier_gi",
        "nounifier_ge",
        "nounifier_im",
        "nounifier_in",
        "nounifier_it",
        "nounifier_inç",
        "nounifier_inti",
        "toolifier_geç",
        "subjectifier_giç",
        "nounifier_anak",
        "nounifier_amak",
        "subjectifier_men",
    }

    def map_candidate(
        self,
        surface: str,
        normalized: str,
        is_proper: bool,
        is_question_particle: bool,
        candidate: dict[str, Any],
    ) -> MorphState:
        suffix_names = [suffix["name"] for suffix in candidate.get("suffixes", [])]
        root_pos = candidate.get("root_pos", "")
        final_pos = candidate.get("final_pos", "")

        if is_question_particle or normalized in {"mı", "mi", "mu", "mü"}:
            category = "MI"
        elif self._is_finite_verb(root_pos, suffix_names):
            category = "VP"
        elif normalized in self.PRONOUN_CASES or final_pos == "cc_pronoun":
            category = self.PRONOUN_CASES.get(normalized, "P1")
        else:
            category = self._nominal_category(suffix_names, is_proper)

        return MorphState(
            category=category,
            root=candidate.get("root", normalized),
            rank=int(candidate.get("rank", 0)),
            score=float(candidate.get("score", 0.0)),
            features={
                "raw_savyar": candidate.get("typing_string", ""),
                "morphology_string": candidate.get("morphology_string", ""),
                "root_pos": root_pos,
                "final_pos": final_pos,
                "suffixes": candidate.get("suffixes", []),
                "suffix_names": suffix_names,
                "case": self._case_name(suffix_names),
            },
        )

    def deduplicate_states(self, states: Iterable[MorphState]) -> list[MorphState]:
        out: list[MorphState] = []
        seen: set[tuple[str, str, tuple[str, ...]]] = set()
        for state in states:
            key = (
                state.category,
                state.root,
                tuple(state.features.get("suffix_names", [])),
            )
            if key in seen:
                continue
            seen.add(key)
            out.append(state)
        return out

    def _is_finite_verb(self, root_pos: str, suffix_names: list[str]) -> bool:
        if root_pos != "verb":
            return False
        if any(name in self.NONFINITE_VERB_TO_NOUN for name in suffix_names):
            finite_after_nominal = any(name in self.FINITE_VERB_SUFFIXES for name in suffix_names)
            if not finite_after_nominal:
                return False
        return any(name in self.FINITE_VERB_SUFFIXES for name in suffix_names)

    def _nominal_category(self, suffix_names: list[str], is_proper: bool) -> str:
        for suffix_name in reversed(suffix_names):
            if suffix_name in self.CASE_TO_CATEGORY:
                return self.CASE_TO_CATEGORY[suffix_name]
        if any(name in self.ADVERBIAL_SUFFIXES for name in suffix_names):
            return "P8"
        if any(name.startswith("possessive_") for name in suffix_names):
            return "P1"
        return "P1" if is_proper else "P2"

    def _case_name(self, suffix_names: list[str]) -> str:
        for suffix_name in reversed(suffix_names):
            if suffix_name in self.CASE_TO_CATEGORY:
                return suffix_name
        return "nominative"

class _DirectSavyar:
    def __init__(self, savyar_dir: Path) -> None:
        self.savyar_dir = savyar_dir
        if not savyar_dir.exists():
            raise SavyarUnavailable(f"Savyar directory not found at {savyar_dir}")
        sys.path.insert(0, str(savyar_dir))

        self.nlp = importlib.import_module("app.nlp_pipeline")
        self.engine = importlib.import_module("app.engine")
        self.sfx = importlib.import_module("util.decomposer")
        closed_class = importlib.import_module("util.words.closed_class")
        ml = importlib.import_module("ml.ml_ranking_model")

        model = ml.SentenceDisambiguator(
            suffix_vocab_size=len(self.sfx.ALL_SUFFIXES),
            closed_class_vocab_size=len(closed_class.CLOSED_CLASS_TOKEN_SPECS),
        )
        with contextlib.redirect_stdout(io.StringIO()):
            self.trainer = ml.Trainer(model, path=str(savyar_dir / "ml" / "model.pt"))

    def analyze(self, tokens: list[Token], top_k: int) -> dict[str, Any]:
        words = [token.normalized for token in tokens if not token.is_question_particle]
        analyses = self.nlp.analyze_words(words, include_closed_class=True)
        if any(not analysis["decomps"] for analysis in analyses):
            missing = [a["word"] for a in analyses if not a["decomps"]]
            raise SavyarUnavailable(f"Savyar could not decompose: {', '.join(missing)}")

        predictions = self.engine.get_top_sentence_predictions(analyses, self.trainer, top_k=top_k)
        word_candidates: dict[str, list[dict[str, Any]]] = {word: [] for word in words}
        for rank, prediction in enumerate(predictions):
            for word_idx, decomp_idx in enumerate(prediction["combo_indices"]):
                analysis = analyses[word_idx]
                word_candidates[analysis["word"]].append(
                    self._candidate_from_analysis(
                        analysis,
                        decomp_idx,
                        rank=rank,
                        score=float(prediction.get("score", 0.0)),
                    )
                )

        payload_tokens: list[dict[str, Any]] = []
        for token in tokens:
            if token.is_question_particle:
                candidates = [
                    {
                        "root": token.normalized,
                        "root_pos": "particle",
                        "final_pos": "question_particle",
                        "suffixes": [],
                        "typing_string": token.normalized,
                        "morphology_string": token.normalized,
                        "rank": 0,
                        "score": 0.0,
                    }
                ]
            else:
                candidates = word_candidates.get(token.normalized, [])
            payload_tokens.append({**token.__dict__, "candidates": candidates})
        return {"tokens": payload_tokens}

    def _candidate_from_analysis(
        self,
        analysis: dict[str, Any],
        decomp_idx: int,
        rank: int,
        score: float,
    ) -> dict[str, Any]:
        root, root_pos, chain, final_pos = analysis["decomps"][decomp_idx]
        vm = analysis["vms"][decomp_idx]
        suffix_forms = self._split_plus(vm.get("suffixes_str", ""))
        suffix_names = self._split_plus(vm.get("names_str", ""))
        suffixes = [
            {
                "name": name,
                "form": suffix_forms[index] if index < len(suffix_forms) else "",
                "makes": getattr(getattr(chain[index], "makes", None), "name", None)
                if index < len(chain)
                else None,
            }
            for index, name in enumerate(suffix_names)
        ]
        return {
            "root": root,
            "root_pos": root_pos,
            "final_pos": final_pos,
            "suffixes": suffixes,
            "typing_string": analysis["typing_strings"][decomp_idx],
            "morphology_string": analysis["typing_strings"][decomp_idx],
            "rank": rank,
            "score": score,
        }

    def _split_plus(self, value: str) -> list[str]:
        if not value:
            return []
        return [part.strip() for part in value.split("+")]