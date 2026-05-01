import copy
import numpy as np
import networkx as nx

from shapely import Polygon, Point, LineString, box
from typing import Dict, List

from src.models.label_candidate import LabelCandidate
from src.topology.faces import node_faces

def restrict_outer_node_candidates(
    G: nx.Graph,
    label_candidates: Dict[int, List[LabelCandidate]],
    convex_hull: List[int],
) -> Dict[int, List[LabelCandidate]]:
    '''
    Restrict the label candidates for nodes on the boundary of the convex hull
    to candidates whose ink_bbox does not intersect with the convex hull.

    Parameters
    ----------
    G : nx.Graph
        graph containing the positions
    label_candidates : Dict[int, List[LabelCandidate]]
        active label candidates
    convex_hull : List[int],
        boundary walk of the convex hull

    Returns
    -------
    filtered_candidates : Dict[int, List[LabelCandidate]]
        remaining label candidates
    '''
    if not convex_hull:
        return label_candidates
    
    hull_coords = np.array([G.nodes[node]['pos'] for node in convex_hull])
    if np.ptp(hull_coords[:, 0]) == 0:
        return label_candidates
    
    hull_poly = Polygon(hull_coords)
    if not hull_poly.is_valid:
        hull_poly = hull_poly.buffer(0)

    filtered_candidates = copy.deepcopy(label_candidates)

    for lid, candidate_list in filtered_candidates.items():
        if not candidate_list:
            continue
        node_pt = Point(G.nodes[label_candidates[lid][0].node_id]['pos'])
        if node_pt.distance(hull_poly.boundary) > 0.25:
            continue

        valid = []
        for candidate in candidate_list:
            candidate_poly = Polygon(candidate.ink_bbox_corners)

            if not hull_poly.contains(candidate_poly) and not hull_poly.intersects(candidate_poly):
                valid.append(candidate)

        filtered_candidates[lid] = valid

    return filtered_candidates

def filter_candidates_by_nodes(
        G: nx.Graph,
        label_candidates: Dict[int, List[LabelCandidate]],
        nodes: List[int],
) -> Dict[int, List[LabelCandidate]]:
    '''
    Remove label candidates whose expanded bounding box intersects with a non-incident node.

    Parameters
    ----------
    G : nx.Graph
        graph containing the positions
    label_candidates : Dict[int, List[LabelCandidate]]
        active label candidates
    nodes : List[int]
        list of nodes

    Returns
    -------
    filtered_candidates : Dict[int, List[LabelCandidate]]
        remaining label candidates
    '''
    filtered_candidates: Dict[int, List[LabelCandidate]] = {}

    for lid, candidates in label_candidates.items():
        surviving = []
        for candidate in candidates:
            (bl_x, bl_y), _, (tr_x, tr_y), _ = candidate.exp_bbox_corners
            occupied = False
            for nid in nodes:
                if nid == candidate.node_id:
                    continue

                ox, oy = G.nodes[nid]['pos']
                if (bl_x <= ox <= tr_x) and (bl_y <= oy <= tr_y):
                    occupied = True
                    break
            
            if not occupied:
                surviving.append(candidate)
                
        filtered_candidates[lid] = surviving

    return filtered_candidates

def filter_candidates_by_edges(
        G: nx.Graph,
        label_candidates: Dict[int, List[LabelCandidate]],
        bounded_faces: List[List[int]]
) -> Dict[int, List[LabelCandidate]]:
    '''
    Remove label candidates whose padding bounding box intersects with graph edges.

    Parameters
    ----------
    G : nx.Graph
        graph containing the positions
    label_candidates : Dict[int, List[LabelCandidate]]
        active label candidates
    bounded_faces : List[List[int]]
        boundary walk of each bounded faces 

    Returns
    -------
    filtered_candidates : Dict[int, List[LabelCandidate]]
        remaining label candidates
    '''
    filtered_candidates: Dict[int, List[LabelCandidate]] = {}

    for node, candidates in label_candidates.items():
        edges = [
            LineString([G.nodes[u]['pos'], G.nodes[v]['pos']])
            for u, v in node_faces(node, bounded_faces)
        ]

        surviving = []
        for candidate in candidates:
            ibl, _, itr, _ = candidate.ink_bbox_corners
            ink_shape = box(ibl[0], ibl[1], itr[0], itr[1])
            pad_shape = ink_shape.buffer(0.01)
            if not any(pad_shape.intersects(e) for e in edges):
                surviving.append(candidate)

        filtered_candidates[node] = surviving

    return filtered_candidates