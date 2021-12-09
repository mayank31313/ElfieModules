from dataclasses import dataclass

@dataclass
class ErrorModel:
    name: str
    error: str
    type: str
    metadata: dict
    timestamp: int
    id: str

