from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Customer:
    first_name: str
    last_name: str
