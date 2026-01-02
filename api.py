from fastapi import APIRouter, Depends

from app.service.lookup_service import PriceLookupService, get_price_lookup_service


router = APIRouter(prefix="/llm")


@router.get("/search")
async def load_llm(
    query: str,
    lookup_service: PriceLookupService = Depends(get_price_lookup_service),
):
    return lookup_service.lookup(query=query)
