# truth_lookup.py
from __future__ import annotations

import os
import sys
from pprint import pprint

from sqlalchemy import create_engine

from app.retrieval.embedder import LlamaIndexHFEmbedder
from app.retrieval.qdrant_indexer import QdrantGadgetIndexer
from app.truth.truth_store import TruthStore
from qdrant_client import QdrantClient, qdrant_client

from config import QDRANT_API_KEY, QDRANT_URL


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python truth_lookup.py "iphone 13 pro max 256gb"')
        return 1

    raw_name = sys.argv[1]

    database_url = (
        "mssql+pyodbc://sa:50610903Da$@localhost:1433/NetworthChecker"
        "?driver=ODBC+Driver+17+for+SQL+Server"
        "&TrustServerCertificate=yes"
    )
    # database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set.")
        print("Example (pyodbc):")
        print(
            "  set DATABASE_URL=mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+17+for+SQL+Server"
        )
        return 1

    # pool_pre_ping avoids stale connections in long-running services
    engine = create_engine(database_url, pool_pre_ping=True)

    store = TruthStore(engine)
    trace = store.debug_get_latest_by_name(raw_name)

    print("I'm not here")

    pprint(trace, sort_dicts=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# iphone xr motherboard
