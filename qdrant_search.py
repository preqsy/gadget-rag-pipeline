# qdrant_search.py
from __future__ import annotations

import os
import sys
from pprint import pprint

from qdrant_client import QdrantClient

from app.retrieval.embedder import LlamaIndexHFEmbedder
from app.retrieval.qdrant_retrieval import QdrantGadgetRetriever
from config import EMBED_MODEL, QDRANT_API_KEY, QDRANT_URL


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python qdrant_search.py "iphnoe 13 pro max 256"')
        return 1

    query = sys.argv[1]

    if not QDRANT_URL or not QDRANT_API_KEY:
        raise RuntimeError("QDRANT_URL or QDRANT_API_KEY is not set")

    qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    embedder = LlamaIndexHFEmbedder()

    retriever = QdrantGadgetRetriever(qdrant=qdrant, embedder=embedder)
    results = retriever.search(query, k=10)

    pprint(
        {
            "query": query,
            "embed_model": EMBED_MODEL,
            "results": results,
        },
        sort_dicts=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
