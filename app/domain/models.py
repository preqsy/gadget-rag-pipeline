# app/domain/models.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class VerifiedPrice:
    """
    VerifiedPrice is a deterministic truth payload.
    It must come only from SQL Server (gadgets table).
    """

    id: int
    name: str
    price: int
    source: str
    scraped_at: datetime
