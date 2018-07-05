import matplotlib.pyplot as plt
import networkx as nx
from typing import Any, Iterator
from collections import defaultdict
from tracktable.analysis.parseTreeNode import *

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

def plot_graph(nxGraph: nx.DiGraph) -> None:
    """
    Plot the graph via matplotlib.
    :see_also: https://matplotlib.org/api/_as_gen/matplotlib.pyplot.scatter.html
    :param nxGraph: The graph to be plotted
    :return: None
    :side_effect: Generates a matplotlib drawing and shows it on the screen.
    """
    pos = graphviz_layout(nxGraph, prog='dot', args='')
    level2_label_coords = {}
    level2_nodes_g = nx.DiGraph(); level2_node_labels = {}
    for val in pos:
        level = int(str(val)[-1])
        try:
            ycoord = plot_graph.switch[level]
        except KeyError:
            level2_label_coords[val] = pos[val]
            level2_nodes_g.add_node(val)
            cat_str = (str(val.category)).split('.')[-1]\
                .replace('_', ' ').title()
            level2_node_labels[val] = str(cat_str)
            # val.key
            continue
        node_coords = pos[val]
        pos[val] = (node_coords[0], ycoord)

    # for n, coords in zip(nxGraph.nodes, pos):
    #     dbg = True
        # try:
        #     temp = nxGraph.node[n]
        #     dbg = True
        # except KeyError as ae:
        #     dbg = True

    plt.figure(figsize=(12, 10))
    nx.draw(nxGraph, pos, node_size=20, alpha=0.5, node_color="blue",
            with_labels=False)
    nx.draw(level2_nodes_g, level2_label_coords, node_size=100, alpha=0.5,
            labels=level2_node_labels, node_color="red", with_labels=True)
    plt.axis('off')
    plt.show()
    # plt.savefig(r'/ascldap/users/pschrum/Documents/Getting Close.png')
plot_graph.switch = {
    0: 10000,
    3: -10000
}

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



