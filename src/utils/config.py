from dataclasses import dataclass
from src.models.label_type import LabelType

@dataclass
class Config:
    dev: bool = True
    file: str = 'living_beings_and_water'
    font_size: str = r'\footnotesize'
    label_config = {
        LabelType.GENERAL: True,
        LabelType.EXTENT:  False,
        LabelType.INTENT:  False
    }
    k_rows: int = 2
    max_row_chars: int = 10