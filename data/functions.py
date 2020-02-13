def f():
    a = 5
    print("testing first")
    g()
    f()


def g():
    l(g)


def l(n):
    f()
