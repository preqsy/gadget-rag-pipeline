# app/db/schema.py
from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime

metadata = MetaData()

gadgets = Table(
    "gadgets",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(255), index=True),
    Column("price", Integer),
    Column("source", String(50)),
    Column("scrapedAt", DateTime),  # DB uses camelCase - keep as-is
)
