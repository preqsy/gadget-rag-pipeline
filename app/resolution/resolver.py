# app/resolution/resolver.py
from __future__ import annotations

from dataclasses import asdict
from difflib import SequenceMatcher
from typing import Any, Dict, List

from app.resolution.model import Candidate, ResolutionResult, ResolvedCandidate

# from app.resolution.models import Candidate, ResolvedCandidate, ResolutionResult


class DeterministicResolver:
    """
    Deterministically resolves a best match from retrieved candidates.
    No LLM involvement. Fully inspectable and debuggable.

    Outputs one of:
      - resolved
      - ambiguous
      - not_found
    """

    def __init__(
        self,
        min_accept_score: float = 0.62,
        min_margin: float = 0.05,
        min_lexical: float = 0.20,
        # Floors for "reasonable retrieval" to decide ambiguous vs not_found
        min_semantic_floor: float = 0.35,
        min_lexical_floor: float = 0.10,
        # Weights
        weight_qdrant: float = 0.7,
        weight_lexical: float = 0.3,
    ):
        total = weight_qdrant + weight_lexical
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"weights must sum to 1.0; got {total}")

        self.min_accept_score = min_accept_score
        self.min_margin = min_margin
        self.min_lexical = min_lexical
        self.min_semantic_floor = min_semantic_floor
        self.min_lexical_floor = min_lexical_floor

        self.weight_qdrant = weight_qdrant
        self.weight_lexical = weight_lexical

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.strip().lower().split())

    @staticmethod
    def _token_jaccard(a: str, b: str) -> float:
        a_tokens = set(a.split())
        b_tokens = set(b.split())
        if not a_tokens or not b_tokens:
            return 0.0
        inter = len(a_tokens & b_tokens)
        union = len(a_tokens | b_tokens)
        return inter / union

    @staticmethod
    def _sequence_similarity(a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio()

    def _lexical_score(self, query: str, candidate_name: str) -> float:
        q = self._normalize(query)
        c = self._normalize(candidate_name)

        jaccard = self._token_jaccard(q, c)
        seq = self._sequence_similarity(q, c)

        # Token overlap matters for product names; seq helps with typos
        return 0.6 * jaccard + 0.4 * seq

    def _combined_score(self, qdrant_score: float, lexical_score: float) -> float:
        return (self.weight_qdrant * qdrant_score) + (
            self.weight_lexical * lexical_score
        )

    def resolve(self, query: str, candidates: List[Candidate]) -> ResolutionResult:
        norm_query = self._normalize(query)

        if not norm_query:
            return ResolutionResult(
                status="not_found",
                selected=None,
                alternatives=[],
                trace={"reason": "empty_query"},
            )

        if not candidates:
            return ResolutionResult(
                status="not_found",
                selected=None,
                alternatives=[],
                trace={"reason": "no_candidates"},
            )

        scored: List[ResolvedCandidate] = []
        for c in candidates:
            lex = self._lexical_score(norm_query, c.name)
            combined = self._combined_score(c.score, lex)
            scored.append(
                ResolvedCandidate(
                    gadget_id=c.gadget_id,
                    name=c.name,
                    qdrant_score=c.score,
                    lexical_score=lex,
                    combined_score=combined,
                )
            )

        scored.sort(key=lambda x: x.combined_score, reverse=True)

        top1 = scored[0]
        top2 = scored[1] if len(scored) > 1 else None
        margin = (
            (top1.combined_score - top2.combined_score) if top2 else top1.combined_score
        )

        acceptable = [
            s
            for s in scored
            if (s.combined_score >= self.min_accept_score)
            and (s.lexical_score >= self.min_lexical)
        ]

        # Determine if retrieval is "reasonable" (for ambiguous fallback)
        reasonable = [
            s
            for s in scored
            if (s.qdrant_score >= self.min_semantic_floor)
            and (s.lexical_score >= self.min_lexical_floor)
        ]

        trace: Dict[str, Any] = {
            "query": query,
            "normalized_query": norm_query,
            "thresholds": {
                "min_accept_score": self.min_accept_score,
                "min_margin": self.min_margin,
                "min_lexical": self.min_lexical,
                "min_semantic_floor": self.min_semantic_floor,
                "min_lexical_floor": self.min_lexical_floor,
                "weight_qdrant": self.weight_qdrant,
                "weight_lexical": self.weight_lexical,
            },
            "top1": asdict(top1),
            "top2": asdict(top2) if top2 else None,
            "margin": margin,
            "acceptable_count": len(acceptable),
            "reasonable_count": len(reasonable),
        }

        # 1) Confident resolution
        if acceptable and (top1 in acceptable) and (margin >= self.min_margin):
            return ResolutionResult(
                status="resolved",
                selected=top1,
                alternatives=scored[1:5],
                trace={**trace, "decision": "resolved_top1_high_confidence"},
            )

        # 2) Ambiguity if we have reasonable candidates but no confident winner
        if reasonable:
            return ResolutionResult(
                status="ambiguous",
                selected=None,
                alternatives=reasonable[:5],
                trace={**trace, "decision": "ambiguous_no_confident_winner"},
            )

        # 3) Otherwise genuinely not found
        return ResolutionResult(
            status="not_found",
            selected=None,
            alternatives=scored[:5],
            trace={**trace, "decision": "not_found_no_reasonable_candidates"},
        )
