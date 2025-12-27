import sys

from qdrant_client import QdrantClient
from sqlalchemy import create_engine
from app.retrieval.embedder import LlamaIndexHFEmbedder
from app.retrieval.qdrant_indexer import QdrantGadgetIndexer
from config import DATABASE_URL, QDRANT_API_KEY, QDRANT_URL


def main():

    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

    qdrant_client = QdrantClient(
        QDRANT_URL,
        api_key=QDRANT_API_KEY,
        timeout=60,
    )
    hug = LlamaIndexHFEmbedder()
    qdrant = QdrantGadgetIndexer(engine=engine, embedder=hug, qdrant=qdrant_client)

    qdrant.index_all()


if __name__ == "__main__":
    raise SystemExit(main())
