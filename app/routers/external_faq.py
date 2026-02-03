from typing import Any

from fastapi import APIRouter

from app.http_client.faq_client import get_faqs, get_faqs_by_id, create_faq

router = APIRouter(prefix="/external-faq", tags=["external-api"])


@router.get("")
async def get_faqs_handler() -> Any:
    return await get_faqs()


@router.get("/{faq_id}")
async def get_faq_by_id_handler(faq_id: int) -> Any:
    return await get_faqs_by_id(faq_id)


@router.post("")
def create_faq_handler(faq: dict[str, Any]) -> Any:
    return create_faq(faq)
