import ast
from ast import dump
import networkx as nx
import matplotlib.pyplot as plt


class VisitNodes(ast.NodeVisitor):
    def __init__(self):
        self.names = []
        self.graph = nx.DiGraph()

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)
        self.graph.add_node(node)

        for child in ast.iter_child_nodes(node):
            self.graph.add_edge(node, child)

    def visit_Name(self, node):
        self.names.append(node.id)


def show_ast(s):
    print(dump(s))


file_py = open('fact.py', 'r')
ast_tree = ast.parse(file_py.read())
print(show_ast(ast_tree))

v = VisitNodes()
v.visit(ast_tree)

nx.draw(v.graph, with_labels=False)
plt.show()


