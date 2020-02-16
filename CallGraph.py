import ast
import csv
import sys
import warnings
import pydot
from ast import dump
from os import path
from random import randint

import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

warnings.filterwarnings("ignore", category=plt.cbook.mplDeprecation)


class CallGraph(ast.NodeVisitor):
    def __init__(self):
        self.graph = nx.DiGraph()
        self.labels = {}

        self.currentFunc = ""
        self.main = "__main__"

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

        if type(node).__name__ == "Module":
            for child in ast.iter_child_nodes(node):
                if type(child).__name__ == "If":
                    for child2 in ast.iter_child_nodes(child):
                        if type(child2).__name__ == "Compare":
                            if child2.left.id == "__name__":
                                for i, j in zip(child2.ops, child2.comparators):
                                    if type(i).__name__ == "Eq" and j.s == "__main__":
                                        self.currentFunc = self.main
                                        self.graph.add_node(self.main)
                                        self.labels[self.main] = self.main
                                        self.get_Children(child)

        if type(node).__name__ == "FunctionDef":
            self.currentFunc = node.name
            self.graph.add_node(node.name)
            self.labels[node.name] = node.name
            self.get_Children(node)

    def get_Children(self, node):
        for child in ast.iter_child_nodes(node):
            if type(child).__name__ == "Call":
                try:
                    self.graph.add_edge(self.currentFunc, child.func.id)
                    self.labels[child.func.id] = child.func.id

                except AttributeError:
                    try:
                        self.graph.add_edge(self.currentFunc, child.func.attr)
                        self.labels[child.func.attr] = child.func.attr

                    except AttributeError:
                        try:
                            self.graph.add_edge(self.currentFunc, child.func.name)
                            self.labels[child.func.name] = child.func.name

                        except AttributeError:
                            self.graph.add_edge(self.currentFunc, child)
                            self.labels[child] = type(child).__name__

            self.get_Children(child)


class VisitNodes(ast.NodeVisitor):
    def __init__(self):
        self.graph = nx.DiGraph()
        self.labels = {}

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

        if type(node).__name__ == "Module":
            self.graph.add_node(node)
            self.labels[node] = type(node).__name__
        else:
            self.graph.add_node(node)

        for child in ast.iter_child_nodes(node):

            if child in self.labels:
                node_name = type(child).__name__
                random_id = randint(1, 10000000)
                new_node = str(node_name) + str(random_id)

                self.graph.add_node(new_node)
                self.labels[new_node] = type(child).__name__
                self.graph.add_edge(node, new_node)

            else:
                if hasattr(child, 'id'):
                    self.graph.add_edge(node, child)
                    self.labels[child] = child.id
                elif hasattr(child, 'name'):
                    self.graph.add_edge(node, child)
                    self.labels[child] = child.name
                elif hasattr(child, 'arg'):
                    self.graph.add_edge(node, child)
                    self.labels[child] = child.arg
                else:
                    if type(child).__name__ == "Num":
                        self.graph.add_edge(node, child)
                        self.labels[child] = child.n
                    if type(child).__name__ == "Str":
                        self.graph.add_edge(node, child)
                        self.labels[child] = child.s
                    else:
                        self.graph.add_edge(node, child)
                        self.labels[child] = type(child).__name__


def show_ast(s):
    print(dump(s))


def draw_graph(parsed_ast, fname, switch, draw):
    v = VisitNodes()
    v.visit(parsed_ast)

    callGraph = CallGraph()
    callGraph.visit(parsed_ast)

    if switch == 0:  # AST
        pos = graphviz_layout(v.graph, prog='dot')

        nx.draw_networkx_nodes(v.graph, pos, node_color='#9999ff')
        nx.draw_networkx_edges(v.graph, pos)
        nx.draw_networkx_labels(v.graph, pos, v.labels, font_size=10)

    if switch == 1:  # Call Graph
        pos2 = graphviz_layout(callGraph.graph, prog='dot')

        nx.draw_networkx_nodes(callGraph.graph, pos2, node_color='#b3ffb3')
        nx.draw_networkx_edges(callGraph.graph, pos2)
        nx.draw_networkx_labels(callGraph.graph, pos2, callGraph.labels, font_size=10)

        file_name = fname.split('.')[0]
        name = file_name.split('/')[1]
        dot_file = name + ".dot"
        image_file = name + ".png"

        image_path = 'CallGraph_images/'
        dot_path = 'CallGraph_dots/'

        nx.drawing.nx_pydot.write_dot(callGraph.graph, dot_path + dot_file)
        (graph,) = pydot.graph_from_dot_file(dot_path + dot_file)
        graph.write_png(image_path + image_file)

    create_csv(v, callGraph, fname)

    if draw:
        plt.show()


def get_mode(labels):
    track = {}

    for key, value in labels.items():
        if value not in track:
            track[value] = 0
        else:
            track[value] += 1

    return max(track, key=track.get)


def create_csv(v, call_graph, fname):
    if not path.exists('results.csv'):
        with open('results.csv', mode='w') as create_file:
            writer = csv.writer(create_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            writer.writerow(['Authour', 'File name', 'Number of nodes.ast', 'Number of edges.ast',
                             'Tree height.ast', 'Most common node.ast', 'Average degree.ast',
                             'Number of nodes.call', 'Number of edges.call', 'Number self loops.call'])
            writer.writerow(["blank", fname, v.graph.number_of_nodes(), v.graph.number_of_edges(),
                             len(nx.dag_longest_path(v.graph)), get_mode(v.labels),
                             v.graph.number_of_edges() / v.graph.number_of_nodes(),
                             call_graph.graph.number_of_nodes(), call_graph.graph.number_of_edges(),
                             call_graph.graph.number_of_selfloops()])

    else:
        with open(r'results.csv', 'a') as file:
            writer = csv.writer(file)
            writer.writerow(["blank", fname, v.graph.number_of_nodes(), v.graph.number_of_edges(),
                             len(nx.dag_longest_path(v.graph)), get_mode(v.labels),
                             v.graph.number_of_edges() / v.graph.number_of_nodes(),
                             call_graph.graph.number_of_nodes(), call_graph.graph.number_of_edges(),
                             call_graph.graph.number_of_selfloops()])


def open_file(file_name):
    return open(file_name, 'r')


if __name__ == "__main__":

    switch = 1
    draw = True

    fname = "data/functions.py"
    file = open_file(fname)
    ast_tree = ast.parse(file.read())
    show_ast(ast_tree)
    draw_graph(ast_tree, fname, switch, draw)

    for fname in sys.argv[1:]:
        file = open_file(fname)
        ast_tree = ast.parse(file.read())
        draw_graph(ast_tree, fname, switch, draw)
