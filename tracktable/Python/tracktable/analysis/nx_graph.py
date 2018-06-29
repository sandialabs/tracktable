import matplotlib.pyplot as plt
import networkx as nx
from typing import Any
from collections import defaultdict

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
    pos = graphviz_layout(nxGraph, prog='dot', args='')
    plt.figure(figsize=(12, 10))
    nx.draw(nxGraph, pos, node_size=20, alpha=0.5, node_color="blue",
            with_labels=False)
    plt.axis('equal')
    plt.show()


if __name__ == '__main__':

    G = nx.balanced_tree(3, 4)
    plot_graph(G)

