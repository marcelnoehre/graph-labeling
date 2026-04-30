from dataclasses import dataclass
from src.models.label_type import LabelType

@dataclass
class Config:
    dev: bool = True
    file: str = 'car'
    font_size: str = r'\footnotesize'
    label_config = {
        LabelType.GENERAL: False,
        LabelType.EXTENT:  True,
        LabelType.INTENT:  True
    }
    k_rows: int = 2
    max_row_chars: int = 10