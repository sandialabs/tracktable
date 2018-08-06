import matplotlib.pyplot as plt
import networkx as nx
from typing import Any, Iterator
from collections import defaultdict
from tracktable.analysis.parseTreeNode import *
import stat
import tracktable.analysis.parseTreeNode as ParseTreeNode
import functools

class TreeDiGraph(nx.DiGraph):

    last_pid = 0

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

    def get_all_by_level(self: nx.DiGraph) -> tuple:
        """
        Performs a "row-based" filter of a tree graph. For every level of a tree
        graph (number of edges from root to a node), returns a list of all nodes
        on that level, then retuns the whole thing in a tuple of those lists.
        :param self: Graph to operate on.
        :return: tuple of all nodes for each level
        """
        node_count = self.number_of_nodes()
        lev_0 = None
        for node in self:
            if node.depth_level == 0:
                lev_0 = Parse_Tree_Root(list(node))
                break

        lev_3 = [n for n in self if n.depth_level == 3]
        lev_1 = []
        lev_2 = []
        l0and3_count = len(lev_0) + len(lev_3) - 1
        if l0and3_count < node_count:
            lev_1 = [n for n in self if n.depth_level == 1]
            lev_2 = [n for n in self if n.depth_level == 2]

        return (lev_0, lev_1, lev_2, lev_3)

    @property
    def trajectory_name(self):
        aTraj = self.my_trajecory
        ts = aTraj[0].timestamp.strftime('%m%d%H%M')
        oid = ts + '_' + aTraj[0].object_id
        return oid

    @property
    def L1catHash(self):
        ret_str = ''
        Lev1: list
        root, Lev1, Lev2, leaves = self.get_all_by_level()
        for a_node in Lev1:
            the_cat = a_node.category
            ret_str += a_node.hash_letter
        return ret_str

    def get_stats_string(self):
        ret_list: list = []
        root, Lev1, Lev2, leaves = self.get_all_by_level()
        traj_name = self.my_trajecory[0].object_id
        ts = str(self.my_trajecory[0].timestamp)
        traj_name = traj_name + '_' + ts[:10]
        traj_name = self.trajectory_name

        ttl_length = self.my_EPL.length_chords()

        max_pct = 0.0
        max_cat = ''

        cruise_segments, cruise_dist_percent, prct = \
            self._compute_a_stat_pair(Lev1, ttl_length, 'Cruise')
        max_pct = prct
        max_cat = 'Cruise'

        turn_segments, turn_dist_percent, prct = \
            self._compute_a_stat_pair(Lev1, ttl_length, 'Course Turn')
        if prct > max_pct:
            max_pct = prct
            max_cat = 'U Turn'

        u_segments, u_dist_percent, prct = \
            self._compute_a_stat_pair(Lev1, ttl_length, 'U Turn')
        if prct > max_pct:
            max_pct = prct
            max_cat = 'U Turn'

        race_segments, race_dist_percent, prct = \
            self._compute_a_stat_pair(Lev1, ttl_length, 'Race Track')
        if prct > max_pct:
            max_pct = prct
            max_cat = 'Race Track'

        s_segments, s_dist_percent, prct = \
            self._compute_a_stat_pair(Lev1, ttl_length, 'S Curve')
        if prct > max_pct:
            max_pct = prct
            max_cat = 'S Curve'

        bous_segments, bous_dist_percent, prct = \
            self._compute_a_stat_pair(Lev1, ttl_length, 'Boustrophedon')
        if prct > max_pct:
            max_pct = prct
            max_cat = 'Boustrophedon'

        nocat_segments, nocat_dist_percent, prct = \
            self._compute_a_stat_pair(Lev1, ttl_length, 'No Cat')
        if prct > max_pct:
            max_pct = prct
            max_cat = 'No Cat'

        ret_str = \
            f'{traj_name},' \
            f'{cruise_segments},{cruise_dist_percent},' \
            f'{turn_segments},{turn_dist_percent},' \
            f'{s_segments},{s_dist_percent},' \
            f'{nocat_segments},{nocat_dist_percent},' \
            f'{bous_segments},{bous_dist_percent},' \
            f'{u_segments},{u_dist_percent},' \
            f'{race_segments},{race_dist_percent},' \
            f'{max_cat},' \
            '\n'
        return ret_str

    _hdr = 'Name,Cruise Count,Cruise Percent,Turn Count, Turn Percent,' \
           'S Curve Count,S Curve Percent,' \
           'No Cat Count,No Cat Percent,Boustophredon Count,' \
           'Boustophredon Percent,' \
           'U Turn Count,U Turn Percent,Race Track Count,Race Track Percent' \
           ',Max Category' \
           '\n'

    def output_short_summary(self: nx.DiGraph, out_file: str) -> None:
        import os, time
        the_dir, the_file = os.path.split(out_file)
        if not os.path.exists(the_dir):
            os.mkdir(the_dir)

        append_or_write = 'at'
        if os.path.exists(out_file):
            # age_seconds = time.time() - os.stat(out_file)[stat.ST_MTIME]
            this_pid = os.getpid()
            if this_pid != TreeDiGraph.last_pid:
                TreeDiGraph.last_pid = this_pid
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
        prct = segs_distance_percent / 100.0
        # prct_str = '%0.2f' % segs_distance_percent + ' %'
        return segs_count, prct, segs_distance_percent


try:
    import pygraphviz
    from networkx.drawing.nx_agraph import graphviz_layout
except ImportError:
    try:
        import pydot
        from networkx.drawing.nx_pydot import graphviz_layout
    except ImportError:
        raise ImportError("Plotting of graphs requires either "
                          "PyGraphviz or pydot. 'pip install pydot' worked"
                          " for me.")
figure_y = 5.0
level2_y_adjustment = 60.0 * figure_y

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
            text_coord_y_adjust = y_multipler * level2_y_adjustment * -1 \
                                * (10.0 / figure_y)
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
        elif level == 0:
            y_multipler = 600.0
            pos[val] = (node_coords[0], ycoord)
            text_coord = pos[val]
            text_coord_y_adjust = y_multipler
            text_coord = text_coord[0], text_coord[1]+text_coord_y_adjust
            label_coords[val] = text_coord
            nodes_g.add_node(val)
            node_labels[val] = nxGraph.name
            continue

    plt.figure(figsize=(12, figure_y))
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
    0: 1000 * figure_y,
    1: 333.3 * figure_y,
    2: -333.3 * figure_y,
    3: -1000 * figure_y
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



