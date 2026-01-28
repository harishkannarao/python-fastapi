from typing import Any

import httpx
from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/external-faq", tags=["external-api"])


@router.get("")
async def get_faqs() -> Any:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.app_external_faq_api_base_url}/faqs")
        return response.json()
