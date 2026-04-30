from typing import Tuple
from dataclasses import dataclass

from src.models.anchor import Anchor
from src.models.label_type import LabelType

@dataclass
class LabelCandidate:
    '''
    One candidate placement for a node label.

    Parameters
    ----------
    node_id : int
        the node assigned to this label
    anchor : Anchor
        which corner or side of the outer bbox is placed at the node position
    label_type : LabelType
        general, extent (objects, below node) or intent (attributes, above node)
    ink_bbox_corners : Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float]]
        ink bbox (BL, BR, TR, TL)
    pad_bbox_corners : Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float]]
        padding bbox (BL, BR, TR, TL)
    exp_bbox_corners : Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float]]
        outer bbox expanded on the free sides (BL, BR, TR, TL)
    center : Tuple[float, float]
        center of the bbox
    text : str
        rendered label content
    '''
    node_id: int
    anchor: Anchor
    label_type: LabelType
    ink_bbox_corners: Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float]]
    pad_bbox_corners: Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float]]
    exp_bbox_corners: Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float]]
    center: Tuple[float, float]
    text: str
