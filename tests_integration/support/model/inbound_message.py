from typing import Any

from pydantic.dataclasses import dataclass

from app.model.response.sample import Sample


@dataclass(frozen=True)
class InboundMessage:
    samples: list[Sample]
    headers: dict[str, Any]
