from dataclasses import dataclass
from src.models.label_type import LabelType

@dataclass
class Config:
    # dev mode
    dev: bool = True
    # data
    file: str = 'living_beings_and_water'    
    label_config = {
        LabelType.GENERAL: True,
        LabelType.EXTENT:  False,
        LabelType.INTENT:  False
    }
    # visualization
    font_size: str = r'\footnotesize'
    k_rows: int = 2
    max_row_chars: int = 10
    # grid
    grid_step: float = 0.5
    min_label_dist: float = 1.0
    max_label_dist: float = 3.0
    top_k: int = 100
    # weights (cost)
    w_align: float = 1.0                # anchor alignment
    w_angle: float = 0.5                # natural angle
    w_boundary: float = 3.0             # close to polygon boundary
    w_binder: float = 10.0              # length of binding line
    w_binder_intersect: float = 100.0   # penalty for binder intersecting another label
    w_binder_cross: float = 8.0         # penalty for crossing binding lines
    w_tight_overlap: float = 80.0       # penalty for ink overlaps 
    w_overlap: float = 10.0             # penalty for padding overlaps
    w_padding: float = 5.0              # penalty for padding
    w_miss: float = 1e6                 # penalty for unplaced label
    w_type: float = 100.0               # penalty for labels in the wrong half space

