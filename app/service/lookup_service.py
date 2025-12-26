from dataclasses import asdict
from typing import Any, Dict
from app.resolution.model import Candidate
from app.resolution.resolver import DeterministicResolver
from app.retrieval.qdrant_retrieval import QdrantGadgetRetriever
from app.truth.truth_store import TruthStore


class PriceLookupService:
    """
    End-to-end pipeline:
      1) Retrieve candidates from Qdrant
      2) Resolve deterministically
      3) Fetch verified price from SQL Server (truth layer)
      4) Return structured output

    Guarantees:
      - price always comes from SQL Server
      - no guessing on ambiguity
      - trace is inspectable
    """

    def __init__(
        self,
        retriever: QdrantGadgetRetriever,
        resolver: DeterministicResolver,
        truth_store: TruthStore,
    ) -> None:
        self.retriever = retriever
        self.resolver = resolver
        self.truth_store = truth_store

    def lookup(
        self,
        query: str,
        k: int = 10,
        debug: bool = True,
    ) -> Dict[str, Any]:
        # 1) Retrieve
        retrieved = self.retriever.search(query, k=k)
        candidates = [Candidate(**r) for r in retrieved]

        # 2) Resolve
        resolution = self.resolver.resolve(query=query, candidates=candidates)

        # 3) Branch
        if resolution.status == "resolved":
            selected = resolution.selected
            assert selected is not None

            verified = self.truth_store.get_latest_by_name(selected.name)

            if verified is None:
                return {
                    "status": "not_found",
                    "query": query,
                    "reason": "resolved_name_not_found_in_sql",
                    "match": asdict(selected),
                    "debug": (
                        {
                            "retrieved": retrieved,
                            "resolution_trace": resolution.trace,
                        }
                        if debug
                        else None
                    ),
                }

            result = {
                "status": "resolved",
                "query": query,
                "match": asdict(selected),
                "verified_price": asdict(verified),
            }

        elif resolution.status == "ambiguous":
            result = {
                "status": "ambiguous",
                "query": query,
                "alternatives": [asdict(a) for a in resolution.alternatives],
            }
        else:
            result = {
                "status": "not_found",
                "query": query,
                "alternatives": [asdict(a) for a in resolution.alternatives],
            }

        if debug:
            result["debug"] = {
                "retrieved": retrieved,
                "resolution_trace": resolution.trace,
            }
        return result
