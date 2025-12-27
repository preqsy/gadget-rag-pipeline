# app/resolution/models.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional

ResolutionStatus = Literal["resolved", "ambiguous", "not_found"]


@dataclass(frozen=True)
class Candidate:
    gadget_id: int
    gadget: str
    score: float


@dataclass(frozen=True)
class ResolvedCandidate:
    gadget_id: int
    gadget: str
    qdrant_score: float
    lexical_score: float
    combined_score: float


@dataclass(frozen=True)
class ResolutionResult:
    status: ResolutionStatus
    selected: Optional[ResolvedCandidate]
    alternatives: List[ResolvedCandidate]
    trace: Dict[str, Any]
