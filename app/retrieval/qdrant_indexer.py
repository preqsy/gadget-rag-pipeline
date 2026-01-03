from typing import Dict, List
from qdrant_client import QdrantClient, qdrant_client
from qdrant_client.http.models import VectorParams, Distance, PointStruct
from sqlalchemy import Engine, select, create_engine

from app.domain.models import GadgetModel
from app.retrieval.embedder import LlamaIndexHFEmbedder
from config import QDRANT_API_KEY, QDRANT_COLLECTION, QDRANT_URL
from app.db.schema import gadgets


class QdrantGadgetIndexer:

    def __init__(
        self, engine: Engine, qdrant: QdrantClient, embedder: LlamaIndexHFEmbedder
    ):
        self.engine = engine
        self.qdrant = qdrant
        self.embedder = embedder

    def ensure_collection(self, vector_size: int):
        existing = {c.name for c in self.qdrant.get_collections().collections}
        if QDRANT_COLLECTION in existing:
            # self.qdrant.delete_collection(QDRANT_COLLECTION)
            return

        self.qdrant.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

    def fetch_all_gadgets(self) -> List[Dict]:
        stmt = select(
            gadgets.c.id,
            gadgets.c.name,
            gadgets.c.price,
            gadgets.c.scrapedAt,
            gadgets.c.source,
        ).order_by(gadgets.c.id.asc())
        with self.engine.connect() as conn:
            rows = conn.execute(stmt).mappings().all()

        return [
            {
                "id": r["id"],
                "name": r["name"],
            }
            for r in rows
        ]

    def index_all(self, batch_size: int = 20):
        items = self.fetch_all_gadgets()
        if not items:
            print("No gadgets found in SQL.")
            return
        first_vec = self.embedder.embed(items[0]["name"])
        self.ensure_collection(vector_size=len(first_vec))

        points: List[PointStruct] = []
        for idx, item in enumerate(items, start=1):
            vec = self.embedder.embed(item["name"])
            points.append(
                PointStruct(
                    id=item["id"],
                    vector=vec,
                    payload={"name": item["name"]},
                )
            )

            if len(points) >= batch_size:
                self.qdrant.upsert(
                    collection_name=QDRANT_COLLECTION,
                    points=points,
                )
                print(f"Upserted {idx}/{len(items)}")
                points = []
        if points:
            self.qdrant.upsert(collection_name=QDRANT_COLLECTION, points=points)
            print(f"Upserted {len(items)}/{len(items)}")

        print("Indexing complete")
