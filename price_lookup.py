# price_lookup.py
from __future__ import annotations

import sys
from pprint import pprint

from sqlalchemy import create_engine
from qdrant_client import QdrantClient

from app.normalizer.llm_normalizer import LLMQueryNormalizer
from config import (
    DATABASE_URL,
    QDRANT_URL,
    QDRANT_API_KEY,
)
from app.retrieval.embedder import LlamaIndexHFEmbedder
from app.retrieval.qdrant_retrieval import QdrantGadgetRetriever
from app.resolution.resolver import DeterministicResolver
from app.truth.truth_store import TruthStore
from app.service.lookup_service import PriceLookupService


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python price_lookup.py "iphone 12 pro 128 gb gold"')
        return 1

    query = sys.argv[1]

    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not set")
    if not QDRANT_URL or not QDRANT_API_KEY:
        raise RuntimeError("QDRANT_URL / QDRANT_API_KEY not set")

    # SQL
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    truth_store = TruthStore(engine)

    # Retrieval
    qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    embedder = LlamaIndexHFEmbedder()
    retriever = QdrantGadgetRetriever(qdrant=qdrant, embedder=embedder)
    llm_normalizer = LLMQueryNormalizer()

    # Resolution
    resolver = DeterministicResolver()

    # Pipeline
    service = PriceLookupService(
        retriever=retriever,
        resolver=resolver,
        truth_store=truth_store,
        normalizer=llm_normalizer,
    )

    output = service.lookup(query, k=10, debug=False)
    pprint(output, sort_dicts=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
