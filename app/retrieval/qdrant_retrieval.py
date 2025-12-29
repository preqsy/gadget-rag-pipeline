from __future__ import annotations
from pprint import pprint

from qdrant_client import QdrantClient

from app.retrieval.embedder import LlamaIndexHFEmbedder
from config import QDRANT_COLLECTION


class QdrantGadgetRetriever:
    """
    Retrieves top-K gadget name candidates from Qdrant by embedding similarity.
    """

    def __init__(self, qdrant: QdrantClient, embedder: LlamaIndexHFEmbedder):
        self.qdrant = qdrant
        self.embedder = embedder

    def search(self, query: str, k: int = 10):
        query = query.strip()
        if not query:
            return []
        query_vector = self.embedder.embed(query)

        results = self.qdrant.query_points(
            collection_name=QDRANT_COLLECTION,
            query=query_vector,
            limit=k,
            with_payload=True,
            with_vectors=False,
        )

        return [
            {
                "gadget_id": r.id,
                "gadget": r.payload.get("gadget") if r.payload else None,
                "score": r.score,
            }
            for r in results.points
        ]
        # pprint(f"Retrieval Result: {results.points[0].vector}")
