import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict

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
    pos = graphviz_layout(G, prog='dot', args='')
    plt.figure(figsize=(12, 10))
    nx.draw(nxGraph, pos, node_size=20, alpha=0.5, node_color="blue",
            with_labels=False)
    plt.axis('equal')
    plt.show()


if __name__ == '__main__':

    G = nx.balanced_tree(3, 4)
    plot_graph(G)

