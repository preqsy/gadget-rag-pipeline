# app/truth/truth_store.py
from __future__ import annotations

from dataclasses import asdict
from typing import Optional

from sqlalchemy import Engine, select

from app.db.schema import gadgets
from app.domain.models import VerifiedPrice


class TruthStore:
    """
    TruthStore is the only allowed component to fetch prices.
    It must be deterministic and SQL-only (no LLM involvement).
    """

    def __init__(self, engine: Engine):
        self.engine = engine

    @staticmethod
    def normalize_name(name: str) -> str:
        # Your DB names are normalized to lowercase
        return name.strip().lower()

    def get_latest_by_name(self, name: str) -> Optional[VerifiedPrice]:
        """
        Deterministically fetch the latest price row for an exact gadget name match.

        Determinism:
          - ORDER BY scrapedAt DESC, id DESC

        Returns:
          - VerifiedPrice if found
          - None if not found
        """
        normalized = self.normalize_name(name)
        if not normalized:
            return None

        stmt = (
            select(
                gadgets.c.id,
                gadgets.c.name,
                gadgets.c.price,
                gadgets.c.source,
                gadgets.c.scrapedAt,
            )
            .where(gadgets.c.name == normalized)
            .order_by(gadgets.c.scrapedAt.desc(), gadgets.c.id.desc())
            .limit(1)
        )

        with self.engine.connect() as conn:
            row = conn.execute(stmt).mappings().first()

        if row is None:
            return None

        # Map scrapedAt -> scraped_at (Python convention)
        return VerifiedPrice(
            id=row["id"],
            name=row["name"],
            price=row["price"],
            source=row["source"],
            scraped_at=row["scrapedAt"],
        )

    def debug_get_latest_by_name(self, name: str) -> dict:
        """
        Debug version that returns a structured trace useful for observability.
        This is helpful as we later integrate RAG steps.
        """
        normalized = self.normalize_name(name)
        result = self.get_latest_by_name(name)

        return {
            "input_name": name,
            "normalized_name": normalized,
            "found": result is not None,
            "verified_price": asdict(result) if result else None,
        }
