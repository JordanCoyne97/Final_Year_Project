def f():
    a = 5
    print("testing first")
    g()
    f()


def g():
    print("test 2")
    l(g)


def l(n):
    f()
