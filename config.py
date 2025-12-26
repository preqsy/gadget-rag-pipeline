import os

QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.TR2Ab5SAc5dOmQy2hhxlLWyh_ZIoNf-DfDvS5Xiy0W0"
QDRANT_URL = (
    "https://2c35ee05-0261-499a-91c6-681d318fd3da.us-east4-0.gcp.cloud.qdrant.io"
)

QDRANT_COLLECTION = "gadgets_name_index"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DATABASE_URL = (
    "mssql+pyodbc://sa:50610903Da$@localhost:1433/NetworthChecker"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&TrustServerCertificate=yes"
)
# from qdrant_client import QdrantClient

# qdrant_client = QdrantClient(
#     url="https://2c35ee05-0261-499a-91c6-681d318fd3da.us-east4-0.gcp.cloud.qdrant.io:6333",
#     api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.TR2Ab5SAc5dOmQy2hhxlLWyh_ZIoNf-DfDvS5Xiy0W0",
# )

# print(qdrant_client.get_collections())
