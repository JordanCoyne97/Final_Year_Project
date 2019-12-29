import ast
from ast import dump
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import warnings
warnings.filterwarnings("ignore", category=plt.cbook.mplDeprecation)


class VisitNodes(ast.NodeVisitor):
    def __init__(self):
        self.names = []
        self.graph = nx.DiGraph()

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

        self.graph.add_node(node)
        #self.graph.add_node(type(node).__name__)

        for child in ast.iter_child_nodes(node):
            self.graph.add_edge(node, child)
            #self.graph.add_edge(type(node).__name__, type(child).__name__)


    def visit_Name(self, node):
        self.names.append(node.id)


def show_ast(s):
    print(dump(s))


def draw_graph(parsed_ast):
    v = VisitNodes()
    v.visit(parsed_ast)

    pos = graphviz_layout(v.graph, prog='dot')
    nx.draw(v.graph, pos, with_labels=False, arrows=True)

    print("Total number of nodes: ", int(v.graph.number_of_nodes()))
    print("Total number of edges: ", int(v.graph.number_of_edges()))
    print("List of all nodes: ", list(v.graph.nodes()))
    print("List of all edges: ", list(v.graph.edges()))
    print("In-degree for all nodes: ", dict(v.graph.in_degree()))
    print("Out degree for all nodes: ", dict(v.graph.out_degree))

    plt.show()


def open_file():
    return open('fact.py', 'r')


if __name__ == "__main__":
    file = open_file()

    ast_tree = ast.parse(file.read())

    draw_graph(ast_tree)
