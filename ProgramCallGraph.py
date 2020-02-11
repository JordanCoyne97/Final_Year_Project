from pycallgraph2 import PyCallGraph
from pycallgraph2.output import GraphvizOutput


def fact(n):
    if n <= 1:
        return 1
    else:
        return n * fact(n - 1)


def Fibonacci(n):
    if n < 0:
        print("Incorrect input")
    elif n == 1:
        return 0
    elif n == 2:
        return 1
    else:
        return Fibonacci(n-1)+Fibonacci(n-2)


def sean():
    A, B, C = sorted(map(int, input().split()))
    order = input()

    for i in range(3):
        if order[i] == 'A':
            print(A, end=' ')
        elif order[i] == 'B':
            print(B, end=' ')
        else:
            print(C, end=' ')


with PyCallGraph(output=GraphvizOutput()):
    Fibonacci(5)
    fact(5)
    sean()
