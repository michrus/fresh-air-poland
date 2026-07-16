from dataclasses import dataclass


@dataclass
class GeneralGIOSAPIParams:
    page: int = 0
    size: int | None = None
