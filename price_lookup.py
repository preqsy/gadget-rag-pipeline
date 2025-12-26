# price_lookup.py
from __future__ import annotations

import sys
from pprint import pprint

from sqlalchemy import create_engine
from qdrant_client import QdrantClient

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

    # Resolution
    resolver = DeterministicResolver()

    # Pipeline
    service = PriceLookupService(
        retriever=retriever, resolver=resolver, truth_store=truth_store
    )

    output = service.lookup(query, k=10, debug=True)
    # pprint(output, sort_dicts=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# {
#     "status": "ambiguous",
#     "query": "iphone",
#     "alternatives": [
#         {
#             "gadget_id": 1615,
#             "name": "apple iphone 6 plus 16 gb gray",
#             "qdrant_score": 0.56405324,
#             "lexical_score": 0.21904761904761905,
#             "combined_score": 0.4605515537142857,
#         },
#         {
#             "gadget_id": 1533,
#             "name": "apple iphone x 64 gb white",
#             "qdrant_score": 0.53206396,
#             "lexical_score": 0.25,
#             "combined_score": 0.447444772,
#         },
#         {
#             "gadget_id": 1602,
#             "name": "apple iphone 8 plus 64 gb white",
#             "qdrant_score": 0.5371397,
#             "lexical_score": 0.21544401544401542,
#             "combined_score": 0.44063099463320465,
#         },
#         {
#             "gadget_id": 1550,
#             "name": "apple iphone 12 pro 128 gb gold",
#             "qdrant_score": 0.5208128,
#             "lexical_score": 0.21544401544401542,
#             "combined_score": 0.4292021646332046,
#         },
#         {
#             "gadget_id": 1627,
#             "name": "apple iphone 8 plus 64 gb black",
#             "qdrant_score": 0.51447797,
#             "lexical_score": 0.21544401544401542,
#             "combined_score": 0.42476778363320455,
#         },
#     ],
#     "debug": {
#         "retrieved": [
#             {
#                 "gadget_id": 1615,
#                 "name": "apple iphone 6 plus 16 gb gray",
#                 "score": 0.56405324,
#             },
#             {
#                 "gadget_id": 1602,
#                 "name": "apple iphone 8 plus 64 gb white",
#                 "score": 0.5371397,
#             },
#             {
#                 "gadget_id": 1533,
#                 "name": "apple iphone x 64 gb white",
#                 "score": 0.53206396,
#             },
#             {
#                 "gadget_id": 1550,
#                 "name": "apple iphone 12 pro 128 gb gold",
#                 "score": 0.5208128,
#             },
#             {
#                 "gadget_id": 1627,
#                 "name": "apple iphone 8 plus 64 gb black",
#                 "score": 0.51447797,
#             },
#             {"gadget_id": 1542, "name": "apple airtag", "score": 0.5126152},
#             {
#                 "gadget_id": 1701,
#                 "name": "apple iphone 16e 128 gb black",
#                 "score": 0.4964003,
#             },
#             {
#                 "gadget_id": 1739,
#                 "name": "apple iphone 12 pro max 256 gb gold",
#                 "score": 0.49144,
#             },
#             {
#                 "gadget_id": 1691,
#                 "name": "apple iphone 11 pro max 64 gb gray",
#                 "score": 0.48602277,
#             },
#             {
#                 "gadget_id": 1624,
#                 "name": "apple iphone 15 pro max 256 gb blue",
#                 "score": 0.478756,
#             },
#         ],
#         "resolution_trace": {
#             "query": "iphone",
#             "normalized_query": "iphone",
#             "thresholds": {
#                 "min_accept_score": 0.62,
#                 "min_margin": 0.05,
#                 "min_lexical": 0.2,
#                 "min_semantic_floor": 0.35,
#                 "min_lexical_floor": 0.1,
#                 "weight_qdrant": 0.7,
#                 "weight_lexical": 0.3,
#             },
#             "top1": {
#                 "gadget_id": 1615,
#                 "name": "apple iphone 6 plus 16 gb " "gray",
#                 "qdrant_score": 0.56405324,
#                 "lexical_score": 0.21904761904761905,
#                 "combined_score": 0.4605515537142857,
#             },
#             "top2": {
#                 "gadget_id": 1533,
#                 "name": "apple iphone x 64 gb white",
#                 "qdrant_score": 0.53206396,
#                 "lexical_score": 0.25,
#                 "combined_score": 0.447444772,
#             },
#             "margin": 0.013106781714285698,
#             "acceptable_count": 0,
#             "reasonable_count": 9,
#             "decision": "ambiguous_no_confident_winner",
#         },
#     },
# }
