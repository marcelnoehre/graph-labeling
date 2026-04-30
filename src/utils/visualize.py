import networkx as nx
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from typing import Dict, List, Tuple

from src.utils.constants import *

def _pos(G: nx.Graph, nid: int, positions: Dict[int, Tuple[float, float]]) -> Tuple[float, float]:
    '''
    Derive position of original and dummy nodes.
    
    Parameters
    ----------
    G : nx.Graph
        graph containing positions
    nid : int
        node to get the position for
    '''
    if nid in G.nodes and 'pos' in G.nodes[nid]:
        return G.nodes[nid]['pos']
    return positions[nid]

def _trim_figure(fig: Figure, ax: Axes) -> None:
    '''
    Trim whitespace around the drawing by:
        1. rasterizing the figure to an RGBA array
        2. finding the bounding box of all non-white pixels
        3. resizing the figure and shifting the axes

    Parameters
    ----------
    fig : Figure
        the figure to trim
    ax : Axes
        the axes of the figure
    '''
    # 1. rasterize
    fig.canvas.draw()
    buf = fig.canvas.buffer_rgba()
    rgba = np.frombuffer(buf, dtype=np.uint8).reshape(fig.canvas.get_width_height()[::-1] + (4,))
    rgb = rgba[:, :, :3]

    # 2. bbox if white px
    is_content = np.any(rgb < 250, axis=2)
    rows = np.any(is_content, axis=1)
    cols = np.any(is_content, axis=0)

    if not rows.any():
        return

    row_min, row_max = np.where(rows)[0][[0, -1]]
    col_min, col_max = np.where(cols)[0][[0, -1]]

    # 3. resize
    dpi = fig.get_dpi()
    fig_w_px, fig_h_px = fig.canvas.get_width_height()
    pad_px = int(round(0.05 * dpi))
    col_min = max(0,        col_min - pad_px)
    col_max = min(fig_w_px, col_max + pad_px)
    row_min = max(0,        row_min - pad_px)
    row_max = min(fig_h_px, row_max + pad_px)
    new_w_in = (col_max - col_min) / dpi
    new_h_in = (row_max - row_min) / dpi
    ax_pos = ax.get_position()
    ax_l_px = ax_pos.x0 * fig_w_px
    ax_b_px = ax_pos.y0 * fig_h_px
    ax_w_px = ax_pos.width  * fig_w_px
    ax_h_px = ax_pos.height * fig_h_px
    crop_b_px = fig_h_px - row_max
    crop_l_px = col_min
    new_ax_l = (ax_l_px - crop_l_px) / (col_max - col_min)
    new_ax_b = (ax_b_px - crop_b_px) / (row_max - row_min)
    new_ax_w = ax_w_px / (col_max - col_min)
    new_ax_h = ax_h_px / (row_max - row_min)

    fig.set_size_inches(new_w_in, new_h_in)
    ax.set_position([new_ax_l, new_ax_b, new_ax_w, new_ax_h])

def plot_graph(
        G: nx.Graph,
        nodes: List[int],
        edges: List[Tuple[int, int]],
        positions: Dict[int, Tuple[float, float]],
        output_path: str,
        title: str = '',
        # data
        intersections: List[Tuple] = [],
        show_intersections: bool = False,
) -> None:
    '''
    Draw the graph and save to a PDF.

    Parameters
    ----------
    TODO
    '''
    fig, ax = plt.subplots(figsize=(8, 6), dpi=DPI)
    fig.canvas.manager.set_window_title(title)

    ##### vertices #####
    for nid in nodes:
        x, y = _pos(G, nid, positions)
        ax.scatter(x, y, facecolor='white', edgecolor='black', linewidth=LINE_WIDTH, s=NODE_SIZE, zorder=100)

    ##### edges #####
    for i, j in edges:
        x0, y0 = _pos(G, i, positions)
        x1, y1 = _pos(G, j, positions)
        ax.plot([x0, x1], [y0, y1], color='black', linewidth=LINE_WIDTH, zorder=2)

    ##### intersections #####
    if show_intersections:
        for pt in intersections:
            ax.scatter(
                pt[0], pt[1], 
                facecolor='white', 
                edgecolor='tab:red', 
                linewidth=LINE_WIDTH, 
                s=NODE_SIZE, 
                zorder=10
            )

    xs = [G.nodes[nid]['pos'][0] for nid in G.nodes]
    ys = [G.nodes[nid]['pos'][1] for nid in G.nodes]
    ax.set_xlim(min(xs) - MARGIN, max(xs) + MARGIN)
    ax.set_ylim(min(ys) - MARGIN, max(ys) + MARGIN)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')
    _trim_figure(fig, ax)

    plt.savefig(output_path, format='pdf')
    plt.close('all')
    plt.close(fig)
