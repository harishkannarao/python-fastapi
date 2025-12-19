import dataclasses


@dataclasses.dataclass(frozen=True)
class Customer:
    first_name: str
    last_name: str
