from data.parser import Parser
from fca.lattice import Lattice

from src.utils.config import Config
from src.topology.planarize import *

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




if __name__ == "__main__":
    main()
