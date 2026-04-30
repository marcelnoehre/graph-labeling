from dataclasses import dataclass

@dataclass
class Config:
    dev: bool = True
    file: str = 'car'