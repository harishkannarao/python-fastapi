from typing import Any

from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/external-faq", tags=["external-api"])


@router.get("")
async def get_faqs() -> dict[str, Any]:
    print(f"Testing >>>>> {settings.app_external_faq_api_base_url}")
    return {"hello": "world"}
