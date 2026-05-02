from src.models.label_candidate import LabelCandidate

def pad_overlap(a: LabelCandidate, b: LabelCandidate) -> bool:
    '''
    True iff the padded boxes of two candidates intersect (touching is not a conflict).

    Parameters
    ----------
    a : LabelCandidate
        first label candidate 
    b : LabelCandidate
        second label candidate

    Returns
    -------
    conflict : bool
        wether the ink boxes overlap
    '''
    (ax0, ay0), _, (ax1, ay1), _ = a.pad_bbox_corners
    (bx0, by0), _, (bx1, by1), _ = b.pad_bbox_corners
    
    return ax0 < bx1 and ax1 > bx0 and ay0 < by1 and ay1 > by0

def bbox_corners(cx, cy, hx, hy):
    '''
    Derive the corner positions based on the center and the half-size
    
    Parameters
    ----------
    cx : float
        x-coordinate of the center
    cy : float
        y-coordinate of the center
    hx : float
        half-width
    hy : float
        half-height

    Returns
    -------
    bbox_corners : Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float]]
        bbox corners based on the center and half-size
    '''
    return (
        (cx - hx, cy - hy), # BL
        (cx + hx, cy - hy), # BR
        (cx + hx, cy + hy), # TR
        (cx - hx, cy + hy), # TL
    )