import networkx as nx

from typing import Dict, List
from shapely import unary_union
from shapely.geometry import Polygon

from src.utils.config import Config
from src.models.label_candidate import LabelCandidate
from src.models.anchor import AnchorType
from src.utils.geometry import *
from src.overflow.grid import *
from src.overflow.hungarian import *

def unbounded_overflow_labels(
        G: nx.Graph,
        label_candidates: Dict[int, List[LabelCandidate]],
        overflow_candidates: Dict[int, LabelCandidate],
        alpha_shape: List[int],
        cfg: Config
    ) -> Tuple[Dict[int, List[Tuple[LabelCandidate, float]]], Dict[int, LabelCandidate]]:
    '''
    Place remaining overflow labels in the graph exterior.

    Parameters
    ----------
    G : nx.Graph
        graph containing positions
    label_candidates : Dict[int, List[LabelCandidate]]
        already placed label candidates
    overflow_candidates : Dict[int, LabelCandidate]
        all overflow candidates
    alpha_shape : List[int]
        boundary walk of the alpha shape
    cfg: Config
        configuration

    Returns
    -------
    grid_candidates, overflow_candidates : Tuple[Dict[int, List[Tuple[LabelCandidate, float]]], Dict[int, LabelCandidate]]
        valid grid candidates, updated ovreflow candidates
    '''
    alpha_pos = [G.nodes[nid]['pos'] for nid in alpha_shape]
    alpha_N = len(alpha_shape)
    alpha_polygon = Polygon(alpha_pos)
    centroid = (alpha_polygon.centroid.x, alpha_polygon.centroid.y)
    placed_union = unary_union([
        Polygon(candidate.exp_bbox_corners)
        for candidates in label_candidates.values()
        for candidate in candidates
    ]) if label_candidates else Polygon()
    node_angles = sorted(
        [(angle_from_centroid(centroid, G.nodes[nid]['pos']), nid) for nid in alpha_shape],
        key=lambda x: x[0]
    )
    gaps = []
    for i in range(alpha_N):
        a_left,  node_left  = node_angles[i]
        a_right, node_right = node_angles[(i + 1) % alpha_N]
        gaps.append({
            'a_left': a_left, 
            'a_right': a_right,
            'gap_size': angular_gap_between(a_left, a_right),
            'node_left': node_left, 
            'node_right': node_right,
            'assigned': []
        })

    # assign unplaced overflow labels to their natural gap
    unplaced_overflow = {
        lid: ol 
        for lid, ol in overflow_candidates.items() 
        if ol.anchor.anchor_type == AnchorType.O
    }
    placed_overflow = {
        lid: ol 
        for lid, ol in overflow_candidates.items() 
        if ol.anchor.anchor_type != AnchorType.O
    }
    for ol in unplaced_overflow.values():
        outward_angle = angle_from_centroid(centroid, ol.center)
        best_gap = max(
            (g for g in gaps if angular_gap_between(g['a_left'], outward_angle) <= g['gap_size']),
            key=lambda g: g['gap_size'],
            default=max(gaps, key=lambda g: g['gap_size'])
        )
        best_gap['assigned'].append(ol.node_id)

    grid_candidates = grid_overflow_candidates(G, label_candidates, overflow_candidates, gaps, centroid, alpha_polygon, placed_union, placed_overflow, cfg)

    assignment = hungarian_solver(G, sorted(grid_candidates.keys()), grid_candidates, cfg)
    for lid, chosen in assignment.items():
        overflow_candidates[lid] = chosen[0]

    return grid_candidates, overflow_candidates
