from typing import Any

from fastapi import APIRouter

from app.http_client.faq_client import get_faqs

router = APIRouter(prefix="/external-faq", tags=["external-api"])


@router.get("")
async def get_faqs_mapping() -> Any:
    return await get_faqs()
