from typing import Tuple
from dataclasses import dataclass

@dataclass
class LabelCandidate:
    '''
    One candidate placement for a node label.

    Parameters
    ----------
    node_id : int
        the node assigned to this label
    anchor : str
        which corner or side of the outer bbox is placed at the node position
    label_type : str
        'general', 'extent' (objects, below node) or 'intent' (attributes, above node)
    bbox_corners : Tuple[Tuple, Tuple, Tuple, Tuple]
        outer bbox (BL, BR, TR, TL) in graph units
    inner_bbox_corners : Tuple[Tuple, Tuple, Tuple, Tuple]
        inner (ink) bbox (BL, BR, TR, TL) in graph units
    expanded_bbox_corners : Tuple[Tuple, Tuple, Tuple, Tuple]
        outer bbox expanded on the two free sides for node exclusion check (BL, BR, TR, TL) in graph units
    center : Tuple[float, float]
        center of the bbox in graph units
    '''
    node_id: int
    anchor: str # 'left' | 'top' | 'top_left' | 'bottom_left' | 'bottom' | 'right' | 'top_right' | 'bottom_right'
    label_type: str # 'general' | 'extent' | 'intent'
    bbox_corners: Tuple[Tuple, Tuple, Tuple, Tuple]
    inner_bbox_corners: Tuple[Tuple, Tuple, Tuple, Tuple]
    expanded_bbox_corners: Tuple[Tuple, Tuple, Tuple, Tuple]
    center: Tuple[float, float]