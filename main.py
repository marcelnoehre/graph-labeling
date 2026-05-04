import copy

from data.parser import Parser
from fca.lattice import Lattice

from src.utils.config import Config
from src.utils.visualize import plot_graph
from src.utils.normalize import *
from src.topology.planarize import *
from src.topology.faces import *
from src.label.generate_candidates import *
from src.filter.filter import *
from src.label.generate_overflow import *
from src.overflow.bounded import *
from src.overflow.unbounded import *

def main():
    cfg = Config()
    parser = Parser()
    
    cxt = parser.decode_cxt(f'data/{cfg.file}.cxt')
    with open(f'data/{cfg.file}.pos', 'r') as f:
        positions = {
            c: tuple(map(float, line.split()[:2]))
            for c, line in enumerate(f) if line.strip()
        }

    lattice = Lattice(cxt)
    nodes = lattice.nodes
    relations = list(lattice.cover_relations())

    # planarize graph
    intersections = find_intersections(relations, positions)
    G = build_planar_graph(relations, positions, intersections)

    # normalize positions
    scale = normalize_positions(G)
    intersection_points = normalize_intersections(G, intersections)
    if cfg.dev:
        plot_graph(
            G, 
            nodes,
            relations,
            output_path='figs/input.pdf'
        )
        plot_graph(
            G, 
            nodes,
            relations,
            output_path='figs/intersections.pdf',
            intersections=intersection_points,
            show_intersections=True
        )

    # faces
    alpha_shape, bounded_faces, areas, centroids = extract_faces(G, scale)
    if cfg.dev:
        plot_graph(
            G, 
            nodes,
            relations,
            output_path='figs/faces.pdf',
            intersections=intersection_points,
            show_intersections=True,
            alpha_shape=alpha_shape,
            show_alpha_shape=True,
            bounded_faces=bounded_faces,
            areas=areas,
            centroids=centroids,
            show_face_areas=True
        )

    # initial set of label candidates
    label_candidates = generate_label_candidates(G, lattice, cfg)
    initial_candidates = copy.deepcopy(label_candidates)
    if cfg.dev:
        plot_graph(
            G, 
            nodes,
            relations,
            output_path='figs/all_label_candidates.pdf',
            label_candidates=label_candidates,
            colored_label_candidates=True,
            show_legend = True
        )

    # filter outer nodes
    label_candidates = restrict_outer_node_candidates(G, label_candidates, alpha_shape)
    if cfg.dev:
        plot_graph(
            G, 
            nodes,
            relations,
            output_path='figs/filtered_outer.pdf',
            label_candidates=label_candidates,
            colored_label_candidates=True
        )

    # filter unclear node assignment
    label_candidates = filter_candidates_by_nodes(G, label_candidates, nodes)
    if cfg.dev:
        plot_graph(
            G, 
            nodes,
            relations,
            output_path='figs/filter_node.pdf',
            label_candidates=label_candidates,
            colored_label_candidates=True
        )

    # filter overlapping edges
    label_candidates = filter_candidates_by_edges(G, label_candidates, bounded_faces)
    if cfg.dev:
        plot_graph(
            G, 
            nodes,
            relations,
            output_path='figs/filter_edges.pdf',
            label_candidates=label_candidates,
            colored_label_candidates=True
        )
    
    # filter by neighbor direction
    label_candidates = filter_candidates_by_neighbor_direction(G, label_candidates, lattice.lattice)
    if cfg.dev:
        plot_graph(
            G, 
            nodes,
            relations,
            output_path='figs/filtered_neighbor.pdf',
            label_candidates=label_candidates,
            colored_label_candidates=True
        )

    # filter by hybrid algorithm
    label_candidates = filter_hyrid(label_candidates)
    if cfg.dev:
        plot_graph(
            G, 
            nodes,
            relations,
            output_path='figs/filtered_hybrid.pdf',
            label_candidates=label_candidates,
            colored_label_candidates=True
        )

    overflow_candidates = generate_overflow_candidates(G, label_candidates, initial_candidates)
    if cfg.dev:
        plot_graph(
            G, 
            nodes,
            relations,
            output_path='figs/all_overflow_candidates.pdf',
            label_candidates=label_candidates,
            colored_label_candidates=True,
            overflow_candidates=overflow_candidates
        )

    overflow_candidates = bounded_overflow_labels(G, label_candidates, overflow_candidates, bounded_faces, centroids)
    if cfg.dev:
        plot_graph(
            G, 
            nodes,
            relations,
            output_path='figs/bounded_overflow_candidates.pdf',
            label_candidates=label_candidates,
            colored_label_candidates=True,
            overflow_candidates=overflow_candidates
        )

    grid_candidates, overflow_candidates = unbounded_overflow_labels(G, label_candidates, overflow_candidates, alpha_shape, cfg)
    if cfg.dev:
        plot_graph(
            G, 
            nodes,
            relations,
            output_path='figs/unbounded_grid_candidates.pdf',
            label_candidates=label_candidates,
            colored_label_candidates=True,
            overflow_candidates=overflow_candidates,
            grid_candidates=grid_candidates
        )
        plot_graph(
            G, 
            nodes,
            relations,
            output_path='figs/unbounded_overflow_candidates.pdf',
            label_candidates=label_candidates,
            colored_label_candidates=True,
            overflow_candidates=overflow_candidates
        )

    plot_graph(
        G, 
        nodes,
        relations,
        output_path=f'figs/{cfg.file}.pdf',
        label_candidates=label_candidates,
        overflow_candidates=overflow_candidates
    )

if __name__ == '__main__':
    main()
