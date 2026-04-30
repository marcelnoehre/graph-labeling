from dataclasses import dataclass

@dataclass
class Config:
    file: str = 'car'
    target_height: float = 10.0