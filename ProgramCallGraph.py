from pycallgraph2 import PyCallGraph
from pycallgraph2.output import GraphvizOutput


def testingMethod(n):
    if n <= 1:
        return 1
    else:
        return n * testingMethod(n - 1)


with PyCallGraph(output=GraphvizOutput()):
    testingMethod(5)
