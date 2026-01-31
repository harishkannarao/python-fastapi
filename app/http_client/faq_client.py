from typing import Any

import httpx

from app.config import settings


async def get_faqs() -> Any:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.app_external_faq_api_base_url}/faqs")
        return response.json()
