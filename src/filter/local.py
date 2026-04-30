import copy
import numpy as np
import networkx as nx

from shapely import Polygon, Point
from typing import Dict, List

from src.models.label_candidate import LabelCandidate

def restrict_outer_node_candidates(
    G: nx.Graph,
    candidates: Dict[int, List[LabelCandidate]],
    convex_hull: List[int],
) -> Dict[int, List[LabelCandidate]]:
    '''
    Restrict the label candidates for nodes on the boundary of the convex hull
    to candidates whose ink_bbox does not intersect with the convex hull.

    Parameters
    ----------
    G : nx.Graph
        graph containing the positions
    candidates : Dict[int, List[LabelCandidate]]
        active label candidates
    convex_hull : List[int],
        boundary walk of the convex hull
    '''
    if not convex_hull:
        return candidates
    
    hull_coords = np.array([G.nodes[node]['pos'] for node in convex_hull])
    if np.ptp(hull_coords[:, 0]) == 0:
        return candidates
    
    hull_poly = Polygon(hull_coords)
    if not hull_poly.is_valid:
        hull_poly = hull_poly.buffer(0)

    filtered_candidates = copy.deepcopy(candidates)

    for lid, candidate_list in filtered_candidates.items():
        if not candidate_list:
            continue
        node_pt = Point(G.nodes[candidates[lid][0].node_id]['pos'])
        if node_pt.distance(hull_poly.boundary) > 0.25:
            continue

        valid = []
        for candidate in candidate_list:
            candidate_poly = Polygon(candidate.ink_bbox_corners)

            if not hull_poly.contains(candidate_poly) and not hull_poly.intersects(candidate_poly):
                valid.append(candidate)

        filtered_candidates[lid] = valid

    return filtered_candidates