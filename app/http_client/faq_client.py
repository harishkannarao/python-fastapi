from typing import Any

import httpx

from app.config import settings


async def get_faqs() -> Any:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.app_external_faq_api_base_url}/faqs")
        return response.json()


async def get_faqs_by_id(faq_id: int) -> Any:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.app_external_faq_api_base_url}/faqs/{faq_id}"
        )
        return response.json()


def create_faq(faq: dict[str, Any]) -> Any:
    with httpx.Client() as client:
        response = client.post(
            f"{settings.app_external_faq_api_base_url}/faqs", json=faq
        )
        return response.json()
