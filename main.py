import copy
import time

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
from src.forces.forces import *

def main():
    init_time = time.perf_counter()
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
    start_time = time.perf_counter()
    intersections = find_intersections(relations, positions)
    G = build_planar_graph(relations, positions, intersections)
    planarize_duration = (time.perf_counter() - start_time) * 1000
    if cfg.runtime:
        print(f"\033[1;36m[RUNTIME]\033[0m Planarize runtime: \033[1;32m{planarize_duration:.2f} ms\033[0m")

    # normalize positions
    scale = normalize_positions(G)
    intersection_points = normalize_intersections(G, intersections)
    if cfg.plot:
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
    start_time = time.perf_counter()
    alpha_shape, bounded_faces, areas, centroids = extract_faces(G, scale)
    topology_duration = (time.perf_counter() - start_time) * 1000
    if cfg.runtime:
        print(f"\033[1;36m[RUNTIME]\033[0m Compute topology: \033[1;32m{topology_duration:.2f} ms\033[0m")
    if cfg.plot:
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
    start_time = time.perf_counter()
    label_candidates = generate_label_candidates(G, lattice, cfg)
    rendering_duration = (time.perf_counter() - start_time) * 1000
    initial_candidates = copy.deepcopy(label_candidates)
    if cfg.runtime:
        print(f"\033[1;36m[RUNTIME]\033[0m Rendering runtime: \033[1;32m{rendering_duration:.2f} ms\033[0m")
    if cfg.plot:
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
    start_time = time.perf_counter()
    label_candidates = restrict_outer_node_candidates(G, label_candidates, alpha_shape)
    filter_out_duration = (time.perf_counter() - start_time) * 1000
    if cfg.runtime:
        print(f"\033[1;36m[RUNTIME]\033[0m Filter out runtime: \033[1;32m{filter_out_duration:.2f} ms\033[0m")
    if cfg.plot:
        plot_graph(
            G, 
            nodes,
            relations,
            output_path='figs/filtered_outer.pdf',
            label_candidates=label_candidates,
            colored_label_candidates=True
        )

    # filter unclear node assignment
    start_time = time.perf_counter()
    label_candidates = filter_candidates_by_nodes(G, label_candidates, nodes)
    filter_node_duration = (time.perf_counter() - start_time) * 1000
    if cfg.runtime:
        print(f"\033[1;36m[RUNTIME]\033[0m Filter node runtime: \033[1;32m{filter_node_duration:.2f} ms\033[0m")
    if cfg.plot:
        plot_graph(
            G, 
            nodes,
            relations,
            output_path='figs/filter_node.pdf',
            label_candidates=label_candidates,
            colored_label_candidates=True
        )

    # filter overlapping edges
    start_time = time.perf_counter()
    label_candidates = filter_candidates_by_edges(G, label_candidates, bounded_faces)
    filter_edge_duration = (time.perf_counter() - start_time) * 1000
    if cfg.runtime:
        print(f"\033[1;36m[RUNTIME]\033[0m Filter edge runtime: \033[1;32m{filter_edge_duration:.2f} ms\033[0m")
    if cfg.plot:
        plot_graph(
            G, 
            nodes,
            relations,
            output_path='figs/filter_edges.pdf',
            label_candidates=label_candidates,
            colored_label_candidates=True
        )
    
    # filter by neighbor direction
    start_time = time.perf_counter()
    label_candidates = filter_candidates_by_neighbor_direction(G, label_candidates, lattice.lattice)
    filter_neighbor_duration = (time.perf_counter() - start_time) * 1000
    if cfg.runtime:
        print(f"\033[1;36m[RUNTIME]\033[0m Filter neighbor runtime: \033[1;32m{filter_neighbor_duration:.2f} ms\033[0m")
    if cfg.plot:
        plot_graph(
            G, 
            nodes,
            relations,
            output_path='figs/filtered_neighbor.pdf',
            label_candidates=label_candidates,
            colored_label_candidates=True
        )

    # filter by hybrid algorithm
    start_time = time.perf_counter()
    label_candidates = filter_hyrid(label_candidates)
    filter_hybrid_duration = (time.perf_counter() - start_time) * 1000
    if cfg.runtime:
        print(f"\033[1;36m[RUNTIME]\033[0m Filter hybrid runtime: \033[1;32m{filter_hybrid_duration:.2f} ms\033[0m")
    if cfg.plot:
        plot_graph(
            G, 
            nodes,
            relations,
            output_path='figs/filtered_hybrid.pdf',
            label_candidates=label_candidates,
            colored_label_candidates=True
        )

    overflow_candidates = generate_overflow_candidates(G, label_candidates, initial_candidates)
    if cfg.plot:
        plot_graph(
            G, 
            nodes,
            relations,
            output_path='figs/all_overflow_candidates.pdf',
            label_candidates=label_candidates,
            colored_label_candidates=True,
            overflow_candidates=overflow_candidates
        )

    start_time = time.perf_counter()
    overflow_candidates = bounded_overflow_labels(G, label_candidates, overflow_candidates, bounded_faces, centroids)
    bounded_overflow_duration = (time.perf_counter() - start_time) * 1000
    if cfg.runtime:
        print(f"\033[1;36m[RUNTIME]\033[0m Bounded overflow runtime: \033[1;32m{bounded_overflow_duration:.2f} ms\033[0m")
    if cfg.plot:
        plot_graph(
            G, 
            nodes,
            relations,
            output_path='figs/bounded_overflow_candidates.pdf',
            label_candidates=label_candidates,
            colored_label_candidates=True,
            overflow_candidates=overflow_candidates
        )

    unbounded: List[int] = [lid for lid, ol in overflow_candidates.items() if ol.anchor.anchor_type == AnchorType.O]
    grid_candidates, overflow_candidates, grid_duration, hungarian_duration = unbounded_overflow_labels(G, label_candidates, overflow_candidates, alpha_shape, cfg)
    if cfg.runtime:
        print(f"\033[1;36m[RUNTIME]\033[0m Grid creation runtime: \033[1;32m{grid_duration:.2f} ms\033[0m")
        print(f"\033[1;36m[RUNTIME]\033[0m Hungarian solver runtime: \033[1;32m{hungarian_duration:.2f} ms\033[0m")
    if cfg.plot:
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

    start_time = time.perf_counter()
    overflow_candidates = optimize_overflow_labels(G, label_candidates, overflow_candidates, unbounded, alpha_shape, cfg)
    force_duration = (time.perf_counter() - start_time) * 1000
    if cfg.runtime:
        print(f"\033[1;36m[RUNTIME]\033[0m Force refinement runtime: \033[1;32m{force_duration:.2f} ms\033[0m")
    if cfg.plot:
        plot_graph(
            G, 
            nodes,
            relations,
            output_path='figs/force_refined.pdf',
            label_candidates=label_candidates,
            colored_label_candidates=True,
            overflow_candidates=overflow_candidates
        )

    total_duration = (time.perf_counter() - init_time) * 1000
    if cfg.runtime:
        print(f"\033[1;36m[RUNTIME]\033[0m Total runtime: \033[1;32m{total_duration:.2f} ms\033[0m")

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
