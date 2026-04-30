from data.parser import Parser
from fca.lattice import Lattice

from src.utils.config import Config
from src.topology.planarize import *
from src.utils.normalize import *

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
    relations = list(lattice.cover_relations())

    # planarize graph
    intersections = find_intersections(relations, positions)
    G = build_planar_graph(relations, positions, intersections)

    # normalize positions
    scale = normalize_positions(G, target_height=10.0)
    intersection_points = normalize_intersections(G, intersections)



if __name__ == "__main__":
    main()
