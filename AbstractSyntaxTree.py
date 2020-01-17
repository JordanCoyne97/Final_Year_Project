import ast
from ast import dump
import matplotlib.pyplot as plt
import networkx as nx
from os import path
import csv
import sys
from networkx.drawing.nx_agraph import graphviz_layout
import warnings
warnings.filterwarnings("ignore", category=plt.cbook.mplDeprecation)


class VisitNodes(ast.NodeVisitor):
    def __init__(self):
        self.names = []
        self.graph = nx.DiGraph()
        self.labels = {}


    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

        self.graph.add_node(node)
        self.labels[node] = type(node).__name__

        for child in ast.iter_child_nodes(node):
            self.graph.add_edge(node, child)
            self.labels[child] = type(child).__name__


    def visit_Name(self, node):
        self.names.append(node.id)


def show_ast(s):
    print(dump(s))


def draw_graph(parsed_ast, fname):
    v = VisitNodes()
    v.visit(parsed_ast)

    pos = graphviz_layout(v.graph, prog='dot')

    nx.draw_networkx_nodes(v.graph, pos, node_color='#9999ff')
    nx.draw_networkx_edges(v.graph, pos)
    nx.draw_networkx_labels(v.graph, pos, v.labels, font_size=10)

    print("Total number of nodes: ", int(v.graph.number_of_nodes()))
    print("Total number of edges: ", int(v.graph.number_of_edges()))
    print("List of all nodes: ", list(v.labels.values()))
    print("List of all edges: ", list(v.graph.edges()))
    # print("In-degree for all nodes: ", dict(v.graph.in_degree))
    # print("Out degree for all nodes: ", dict(v.graph.out_degree))

    create_csv(v, fname)
    #plt.show()


def create_csv(v, fname):

    if not path.exists('results.csv'):
        with open('results.csv', mode='w') as create_file:
            writer = csv.writer(create_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            writer.writerow(['Authour', 'File name', 'Number of nodes', 'Number of edges'])
            writer.writerow(["blank", fname, v.graph.number_of_nodes(), v.graph.number_of_edges()])
    else:
        with open(r'results.csv', 'a') as file:
            writer = csv.writer(file)
            writer.writerow(["blank", fname, v.graph.number_of_nodes(), v.graph.number_of_edges()])


def open_file(file_name):
    return open(file_name, 'r')


if __name__ == "__main__":
    fname = "fact.py"
    file = open_file(fname)
    ast_tree = ast.parse(file.read())
    draw_graph(ast_tree, fname)

    # for fname in sys.argv[1:]:
    #     file = open_file(fname)
    #     ast_tree = ast.parse(file.read())
    #     draw_graph(ast_tree, fname)
