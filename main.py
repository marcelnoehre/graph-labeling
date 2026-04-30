from data.parser import Parser
from fca.lattice import Lattice

from src.utils.config import Config
from src.utils.visualize import plot_graph
from src.utils.normalize import *
from src.topology.planarize import *
from src.topology.faces import *
from src.label.generate_candidates import *
from src.filter.local import *

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
            output_path="figs/input.pdf"
        )
        plot_graph(
            G, 
            nodes,
            relations,
            output_path="figs/intersections.pdf",
            intersections=intersection_points,
            show_intersections=True
        )

    # faces
    convex_hull, bounded_faces, areas, centroids = extract_faces(G, scale)
    if cfg.dev:
        plot_graph(
            G, 
            nodes,
            relations,
            output_path="figs/faces.pdf",
            intersections=intersection_points,
            show_intersections=True,
            convex_hull=convex_hull,
            show_convex_hull=True,
            bounded_faces=bounded_faces,
            areas=areas,
            centroids=centroids,
            show_face_areas=True
        )

    label_candidates = generate_label_candidates(G, lattice, cfg)
    if cfg.dev:
        plot_graph(
            G, 
            nodes,
            relations,
            output_path="figs/all_label_candidates.pdf",
            label_candidates=label_candidates,
            colored_label_candidates=True,
            show_legend = True
        )

    label_candidates = restrict_outer_node_candidates(G, label_candidates, convex_hull)
    if cfg.dev:
        plot_graph(
            G, 
            nodes,
            relations,
            output_path="figs/filtered_outer.pdf",
            label_candidates=label_candidates,
            colored_label_candidates=True,
            show_legend = True
        )

if __name__ == "__main__":
    main()
