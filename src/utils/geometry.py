from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List, Tuple

import numpy as np
import networkx as nx

from shapely.geometry import LineString, Point, Polygon

from src.utils.constants import NODE_RADIUS
from src.models.anchor import Anchor

if TYPE_CHECKING:
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

def label_wh(corners: Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float]]) -> Tuple[float, float]:
    '''
    Bbox dimensions.

    Parameters
    ----------
    corners : Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float], Tuple[float, float]]
        bbox corners
    
    Returns
    -------
    width, height : Tuple[float, float]
        size of the given label
    '''
    bl, br, _, tl = corners
    return abs(br[0] - bl[0]), abs(tl[1] - bl[1])


def bbox_polygon(cx: float, cy: float, w: float, h: float) -> Polygon:
    '''
    Create a polygon for a given bbox bbox centered at (cx, cy) with width w and height h.

    Parameters
    ----------
    cx : float 
        x-coordinate of center
    cy : float 
        y-coordinate of center
    w : float
        desired width 
    h : float
        desired height

    Returns
    -------
    bbox_poly : Polygon
        bbox polygon derived from center and size 
    '''
    hw, hh = w / 2, h / 2
    return Polygon([
        (cx - hw, cy - hh), (cx + hw, cy - hh),
        (cx + hw, cy + hh), (cx - hw, cy + hh),
    ])

def binding_line_valid(
    G: nx.Graph,
    lid: int,
    anchor: Anchor,
    label_candidates: Dict[int, List[LabelCandidate]],
    overflow_candidates: Dict[int, LabelCandidate],
    placed_overflow: List[int],
    soft: bool = False,
    max_edge_crossings: int = -1
) -> bool:
    '''
    Check wether a binding line is valid.

    Parameters
    ----------
    G : nx.Graph
        graph containing positions
    lid : int
        label the binding line is attached to
    anchor : Anchor
        chosen anchor
    label_candidates : Dict[int, List[LabelCandidate]]
        already placed labels
    overflow_candidates : Dict[int, LabelCandidate]
        overflow candidates to be placed
    placed_overflow : List[Dict[int, Tuple[float, float], LineString]]
        already placed overflow candidates
    soft : bool = False
        soft mode is less restrictive
    max_edge_crossings : int = -1
        restrict max number of edge crossings

    Returns
    valid : bool
        wether the binding line is valid
    '''
    ol = overflow_candidates[lid]
    binding_line = LineString([anchor.pos, G.nodes[ol.node_id]['pos']])

    for o_lid in placed_overflow:
        if o_lid == lid:
            continue

        o_ol = overflow_candidates[o_lid]
        o_cx, o_cy = G.nodes[o_ol.node_id]['pos']
        w, h = label_wh(overflow_candidates[o_lid].exp_bbox_corners)

        # binder intersects already placed overflow label
        if binding_line.intersects(bbox_polygon(o_cx, o_cy, w, h)):
            return False
        
        # binder conflicts with another binder
        if not soft:
            if binding_line.crosses(LineString([o_ol.anchor.pos, (o_cx, o_cy)])):
                return False
    
    for candidates in label_candidates.values():
        for cand in candidates:
            ink_poly = Polygon(cand.ink_bbox_corners).buffer(0)
            pad_poly = Polygon(cand.pad_bbox_corners).buffer(0)

            if soft:
                # binder intersects ink bbox of a label
                if binding_line.intersects(ink_poly):
                    return False
            else:
                # binder intersects padded bbox of a label
                if binding_line.intersects(pad_poly):
                    return False

    for nid, data in G.nodes(data=True):
        if nid == ol.node_id:
            continue
        if not isinstance(nid, int):
            continue
        
        # binder intersects with another node
        if binding_line.distance(Point(data['pos'])) < NODE_RADIUS:
            return False
        
    if max_edge_crossings >= 0:
        # restrict the number of edge crossings 
        crossings = 0
        for u, v in G.edges():
            if binding_line.crosses(LineString([G.nodes[u]['pos'], G.nodes[v]['pos']])):
                crossings += 1
                
            if crossings > max_edge_crossings:
                return False

    # valid - no conflict found
    return True