import matplotlib.pyplot as plt
import networkx as nx
from typing import Any, Iterator
from collections import defaultdict
from tracktable.analysis.parseTreeNode import *
import stat
import tracktable.analysis.parseTreeNode as ParseTreeNode
import functools

class TreeDiGraph(nx.DiGraph):

    _root_node: Any = None
    @property
    def root_node(self):
        if self._root_node:
            return self._root_node
        else:
            try:
                for n in self.nodes:
                    predecessors = self.pred[n]
                    if len(self.pred[n]) == 0:
                        self._root_node = n
                        break
            except IndexError:
                self._root_node = None
            return self._root_node

    @property
    def csv_report(self):
        root: Parse_Tree_Root = self.root_node
        header_str = root.report_header_string(self)
        data_str = root.report_data_lines(self)
        return header_str + data_str

    def get_stats_string(self):
        ret_list = []
        root, Lev1, Lev2, leaves = ParseTreeNode.get_all_by_level(self)

        traj_name = self.my_trajecory[0].object_id
        ts = str(self.my_trajecory[0].timestamp)
        traj_name = traj_name + '_' + ts[:10]

        ttl_length = self.my_EPL.length_chords()

        cruise_segments, cruise_dist_percent = \
            self._compute_a_stat_pair(Lev1, ttl_length, 'Cruise')

        u_segments, u_dist_percent = \
            self._compute_a_stat_pair(Lev1, ttl_length, 'U Turn')

        race_segments, race_dist_percent = \
            self._compute_a_stat_pair(Lev1, ttl_length, 'Race Track')

        s_segments, s_dist_percent = \
            self._compute_a_stat_pair(Lev1, ttl_length, 'S Curve')

        bous_segments, bous_dist_percent = \
            self._compute_a_stat_pair(Lev1, ttl_length, 'Boustrophedon')

        nocat_segments, nocat_dist_percent = \
            self._compute_a_stat_pair(Lev1, ttl_length, 'No Cat')

        ret_str = \
            f'{traj_name},' \
            f'{cruise_segments},{cruise_dist_percent},' \
            f'{s_segments},{s_dist_percent},' \
            f'{nocat_segments},{nocat_dist_percent},' \
            f'{bous_segments},{bous_dist_percent},' \
            f'{u_segments},{u_dist_percent},' \
            f'{race_segments},{race_dist_percent},' \
            '\n'
        return ret_str

    _hdr = 'Name,Cruise Count,Cruise Percent,S Curve Count,S Curve Percent,' \
           'No Cat Count,No Cat Percent,Boustophredon Count,' \
           'Boustophredon Percent,' \
           'U Turn Count,U Turn Percent,Race Track Count,Race Track Percent' \
           '\n'

    def output_short_summary(self: nx.DiGraph, out_file: str) -> None:
        import os, time
        the_dir, the_file = os.path.split(out_file)
        if not os.path.exists(the_dir):
            os.mkdir(the_dir)

        append_or_write = 'at'
        if os.path.exists(out_file):
            age_seconds = time.time() - os.stat(out_file)[stat.ST_MTIME]
            if age_seconds > 12.0:  # seconds
                append_or_write = 'wt'
        else:
            append_or_write = 'wt'

        with open(out_file, append_or_write) as outf:
            if 'w' in append_or_write:
                outf.write(self._hdr)
            outf.write(self.get_stats_string())
            outf.flush()


    def _compute_a_stat_pair(self, collection, ttl_len, cat_str):
        segs = [x for x in collection if x.category_str == cat_str]
        segs_count = len(segs)
        segs_distance_percent = 100.0 * \
                                functools.reduce(
                                    lambda acc, seg: acc + seg.length_chords,
                                    segs, 0.0) / \
                                ttl_len
        prct_str = '%0.2f' % segs_distance_percent + ' %'
        return segs_count, prct_str


try:
    import pygraphviz
    from networkx.drawing.nx_agraph import graphviz_layout
except ImportError:
    try:
        import pydot
        from networkx.drawing.nx_pydot import graphviz_layout
    except ImportError:
        raise ImportError("This example needs Graphviz and either "
                          "PyGraphviz or pydot. 'pip install pydot' worked"
                          " for me.")

level2_y_adjustment = 600.0

def plot_graph(nxGraph: nx.DiGraph) -> None:
    """
    Plot the graph via matplotlib.
    :see_also: https://matplotlib.org/api/_as_gen/matplotlib.pyplot.scatter.html
    :param nxGraph: The graph to be plotted
    :return: None
    :side_effect: Generates a matplotlib drawing and shows it on the screen.
    """
    pos = graphviz_layout(nxGraph, prog='dot', args='')
    label_coords = {}
    nodes_g = nx.DiGraph(); node_labels = {}
    l1_adj_counter = 0
    for val in pos:
        level = int(str(val)[-1])
        ycoord = plot_graph.switch[level]
        node_coords = pos[val]
        pos[val] = (node_coords[0], ycoord)
        if level == 2:
            try:
                y_multipler = val.category.value[0]
            except TypeError:
                y_multipler = val.category.value
            pos[val] = (node_coords[0], ycoord)
            text_coord = pos[val]
            text_coord_y_adjust = y_multipler * level2_y_adjustment * -1
            text_coord = text_coord[0], text_coord[1]+text_coord_y_adjust
            label_coords[val] = text_coord
            nodes_g.add_node(val)
            cat_str = (str(val.category)).split('.')[-1]\
                .replace('_', ' ').title()
            node_labels[val] = str(cat_str)
            continue
        elif level == 1:
            l1_adj_counter += 1
            y_multipler = 600.0
            pos[val] = (node_coords[0], ycoord)
            text_coord = pos[val]
            level1_y_adjustment = (l1_adj_counter % 3) - 1
            text_coord_y_adjust = y_multipler * level1_y_adjustment * -1
            text_coord = text_coord[0], text_coord[1]+text_coord_y_adjust
            label_coords[val] = text_coord
            nodes_g.add_node(val)
            cat_str = (str(val.category)).split('.')[-1]\
                .replace('_', ' ').title()
            node_labels[val] = str(cat_str)
            continue

    plt.figure(figsize=(12, 10))
    nx.draw(nxGraph, pos, node_size=20, alpha=0.5, node_color="blue",
            with_labels=False)

    nx.draw_networkx_labels(nxGraph, label_coords, node_labels,
                            font_size=10,
                            bbox=dict(boxstyle="square",
                                      ec='k',
                                      fc=(0.5, 0.5, 0.5, 0.10),))
    # for nx draw labels see
    # https://networkx.github.io/documentation/networkx-2.0/reference/generate
    # d/networkx.drawing.nx_pylab.draw_networkx_labels.html
    # for matplotlib bounding boxes see
    # https://matplotlib.org/gallery/shapes_and_collections/fancybox_demo.html

    plt.axis('off')
    plt.show()
    # plt.savefig(r'/ascldap/users/pschrum/Documents/Getting Close.png')
plot_graph.switch = {
    0: 10000,
    1: 3333,
    2: -3333,
    3: -10000
}

# def output_short_summary(g :nx.DiGraph, out_file: str) -> None:
#     import os
#     the_dir, the_file = os.path.split(out_file)
    # if not os.path.exists(the_dir)
    #     os.mkdir(the_dir, mode=)


def leaves_gen(g :nx.DiGraph) -> Iterator[Parse_Tree_Leaf]:
    a_node: Parse_Tree_Node
    for a_node in g:
        if a_node is Parse_Tree_Leaf:
            yield a_node


def depth_level_x_gen(g :nx.DiGraph, depth_level :int) \
        -> Iterator[Parse_Tree_Node]:
    """
    Given a tree graph (single root node), yield only nodes that are at a
        given depth level. Note, this function needs to be optimized.
    :param g: The tree graph to operate on
    :param depth_level: The depth level to reach for
    :return: yield nodes at indicated depth level
    """
    a_node: Parse_Tree_Node
    for a_node in g:
        if a_node.depth_level == depth_level:
            yield a_node


if __name__ == '__main__':

    G = nx.balanced_tree(3, 4)
    plot_graph(G)



