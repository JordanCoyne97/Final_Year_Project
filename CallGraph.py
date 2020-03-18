import ast
import csv
import sys
import warnings

import pydot
import requests
import os
from ast import dump
from bs4 import BeautifulSoup
from os import path
from random import randint

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from networkx.drawing.nx_agraph import graphviz_layout

warnings.filterwarnings("ignore", category=plt.cbook.mplDeprecation)
warnings.filterwarnings("ignore", category=RuntimeWarning)


class CallGraph(ast.NodeVisitor):
    def __init__(self):
        self.graph = nx.DiGraph()
        self.labels = {}

        self.module = "Module"
        self.currentFunc = ""
        self.currentClass = ""

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

        if type(node).__name__ == "Module":
            for child in ast.iter_child_nodes(node):
                if type(child).__name__ == "If":
                    for child2 in ast.iter_child_nodes(child):
                        if type(child2).__name__ == "Compare":
                            try:
                                if child2.left.id == "__name__":
                                    for i, j in zip(child2.ops, child2.comparators):
                                        if type(i).__name__ == "Eq" and j.s == "__main__":
                                            self.currentFunc = self.module
                                            self.graph.add_node(self.module)
                                            self.labels[self.module] = self.module
                                            self.get_Children(child)
                            except AttributeError:
                                print("Error with attribute while visiting main class (Call Graph). ")

                if type(child).__name__ == "ClassDef":
                    #  uncomment to print class.init instead of class.name
                    self.currentClass = child.name  # + ".__init__"
                    self.labels[self.currentClass] = self.currentClass

                    self.graph.add_edge(self.module, self.currentClass)

                    for child2 in ast.iter_child_nodes(child):
                        if type(child2).__name__ == "FunctionDef":
                            if not child2.name == "__init__":
                                self.currentFunc = child2.name
                                self.labels[self.currentFunc] = child2.name
                                self.graph.add_edge(self.currentClass, self.currentFunc)

        if type(node).__name__ == "FunctionDef" and not node.name == "__init__":
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
                    # Prints the whole string e.g print("all of this will show on the ast graph")
                    # if type(child).__name__ == "Str":
                    #     self.graph.add_edge(node, child)
                    #     self.labels[child] = child.s
                    else:
                        self.graph.add_edge(node, child)
                        self.labels[child] = type(child).__name__


def draw_graph(parsed_ast, fname, switch, draw):
    ast = VisitNodes()
    ast.visit(parsed_ast)

    callGraph = CallGraph()
    callGraph.visit(parsed_ast)

    if switch == 1:  # AST draw graph
        plt.figure(figsize=(14, 6.6))
        pos = graphviz_layout(ast.graph, prog='dot')

        nx.draw_networkx_nodes(ast.graph, pos, node_color='#9999ff')
        nx.draw_networkx_edges(ast.graph, pos)
        nx.draw_networkx_labels(ast.graph, pos, ast.labels, font_size=10)

    if switch == 2:  # Call Graph draw graph
        plt.figure(figsize=(14, 6.6))
        pos2 = graphviz_layout(callGraph.graph, prog='dot')

        nx.draw_networkx_nodes(callGraph.graph, pos2, node_color='#b3ffb3')
        nx.draw_networkx_edges(callGraph.graph, pos2)
        nx.draw_networkx_labels(callGraph.graph, pos2, callGraph.labels, font_size=10)

    if switch == 0:  # Pass both (draw neither)
        pass

    save_graph_images(fname, callGraph, ast)
    create_csv(ast, callGraph, fname)

    if draw == 1:
        plt.tight_layout()
        plt.show()


def save_graph_images(fname, callGraph, ast):
    file_name = fname.split('.')[0]
    name = file_name.split('/')[1]
    dot_file = name + ".dot"
    image_file = name + ".png"

    ast_image_path = 'AST_images/'
    ast_dot_path = 'AST_dots/'

    call_image_path = 'CallGraph_images/'
    call_dot_path = 'CallGraph_dots/'

    # #  save ast graph as .png
    # nx.drawing.nx_pydot.write_dot(ast.graph, ast_dot_path + dot_file)
    # (graph,) = pydot.graph_from_dot_file(ast_dot_path + dot_file)
    # graph.write_png(ast_image_path + image_file)

    # save call graph as .png
    nx.drawing.nx_pydot.write_dot(callGraph.graph, call_dot_path + dot_file)
    (graph,) = pydot.graph_from_dot_file(call_dot_path + dot_file)
    graph.write_png(call_image_path + image_file)


def find_url_from_csv(target_file):
    data = pd.read_csv("Python_Recipes.csv")
    pd.set_option('display.max_colwidth', 1000)

    target_row = data.loc[data["File Name"] == target_file]
    url = target_row["URL"].to_string(index=False)

    return url


def web_scraper(url):
    if url is None:
        return

    source = requests.get(url).text
    soup = BeautifulSoup(source, 'html5lib')

    tags = soup.find("ul", class_="nomachinetags flat")
    tags_list = list(tags.stripped_strings)

    author_details = soup.find("table", class_="gravatar")
    author_name = author_details.a.text

    return tags_list, author_name


def create_csv(ast, call_graph, fname):
    if not path.exists('results.csv'):
        with open('results.csv', mode='w') as create_file:
            writer = csv.writer(create_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            writer.writerow(['Author', 'Tags', 'File name', 'Number of nodes.ast', 'Number of edges.ast',
                             'Tree height.ast', 'Number of nodes.call', 'Number of edges.call',
                             'Impurity of tree.call', 'Number of self loops.call'])

            target_name = fname.split('/')[1]
            url = find_url_from_csv(target_name)
            tags, author = web_scraper(url)

            writer.writerow([author, tags, target_name, ast.graph.number_of_nodes(), ast.graph.number_of_edges(),
                             len(nx.dag_longest_path(ast.graph)), call_graph.graph.number_of_nodes(),
                             call_graph.graph.number_of_edges(),
                             get_tree_impurity(call_graph.graph), call_graph.graph.number_of_selfloops()])

    else:
        with open(r'results.csv', 'a') as file:
            writer = csv.writer(file)

            target_name = fname.split('/')[1]
            url = find_url_from_csv(target_name)
            tags, author = web_scraper(url)

            writer.writerow([author, tags, target_name, ast.graph.number_of_nodes(), ast.graph.number_of_edges(),
                             len(nx.dag_longest_path(ast.graph)),
                             call_graph.graph.number_of_nodes(), call_graph.graph.number_of_edges(),
                             get_tree_impurity(call_graph.graph), call_graph.graph.number_of_selfloops()])


def get_tree_impurity(G):
    greater_than_one = 0

    for node in G:
        if G.in_degree(node) > 1:
            greater_than_one = greater_than_one + 1

    tree_impurity = greater_than_one / G.__len__()
    return round(tree_impurity, 3)


def create_stats_figures():
    if path.exists('results.csv'):
        data = pd.read_csv("results.csv")

        data.plot(kind='scatter', x='Number of nodes.ast', y='Number of nodes.call', color='magenta')
        plt.suptitle('Scatter plot comparing number of nodes')
        plt.savefig('Stats/number of ast vs call nodes.png')

        data.plot(kind='scatter', x='Number of nodes.ast', y='Tree height.ast', color='blue')
        plt.suptitle('Scatter plot comparing ast nodes to tree height')
        plt.savefig('Stats/ast nodes vs tree height.png')

        for column in data:
            plt.clf()
            current_df = data[column].copy()
            current_df.hist()
            plt.suptitle(str(column) + ' histogram')
            plt.savefig('Stats/' + str(column) + ' hist.png')


def create_overall_table():
    if path.exists('results.csv'):
        data = pd.read_csv("results.csv")

        for column in data:
            try:
                mean = data[column].mean()
                max = data[column].max()
                min = data[column].min()
                std = data[column].std()

                if not path.exists('average_table.csv'):
                    with open('average_table.csv', mode='w') as create_file:
                        writer = csv.writer(create_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                        writer.writerow(['Column', 'Min', 'Max', 'Mean', 'Std'])
                        writer.writerow([column, round(min, 3), round(max, 3), round(mean, 3), round(std, 3)])

                else:
                    with open(r'average_table.csv', 'a') as file:
                        writer = csv.writer(file)

                        writer.writerow([column, round(min, 3), round(max, 3), round(mean, 3), round(std, 3)])

            except TypeError:
                pass  # pass if it doesn't have numeric column


def reset_results(file_to_remove):
    if path.exists(file_to_remove):
        os.remove(file_to_remove)


def open_file(file_name):
    return open(file_name, 'r')


def show_ast(s):
    print(dump(s))


if __name__ == "__main__":

    switch = int(sys.argv[1])
    draw = int(sys.argv[2])

    reset_results('results.csv')

    for fname in sys.argv[3:]:
        file = open_file(fname)
        print("Processing: " + str(fname) + " ...")
        ast_tree = ast.parse(file.read())
        draw_graph(ast_tree, fname, switch, draw)

    create_stats_figures()

    reset_results('average_table.csv')
    create_overall_table()
