from pycallgraph2 import PyCallGraph
from pycallgraph2.output import GraphvizOutput


def testingMethod(n):
    if n <= 1:
        return 1
    else:
        return n * testingMethod(n - 1)


def do_foo():
    return open('fact.py', 'r')


with PyCallGraph(output=GraphvizOutput()):
    open('fact.py', 'r')