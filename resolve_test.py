# resolve_test.py
from __future__ import annotations

import sys
from pprint import pprint

from qdrant_client import QdrantClient

from app.resolution.model import Candidate
from app.retrieval.embedder import LlamaIndexHFEmbedder
from app.retrieval.qdrant_retrieval import QdrantGadgetRetriever
from config import QDRANT_API_KEY, QDRANT_URL
from app.resolution.resolver import DeterministicResolver


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python resolve_test.py "iphone 12 pro 128 gb gold"')
        return 1

    query = sys.argv[1]

    qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    embedder = LlamaIndexHFEmbedder()
    retriever = QdrantGadgetRetriever(qdrant=qdrant, embedder=embedder)

    raw_results = retriever.search(query, k=10)
    candidates = [Candidate(**r) for r in raw_results]

    resolver = DeterministicResolver()
    resolution = resolver.resolve(query=query, candidates=candidates)

    pprint(
        {
            "query": query,
            "retrieved": raw_results,
            "resolution_status": resolution.status,
            "selected": resolution.selected,
            "alternatives": resolution.alternatives,
            "trace": resolution.trace,
        },
        sort_dicts=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
