A, B, C = sorted(map(int, input().split()))
order = input()

for i in range(3):
    if order[i] == 'A':
        print(A, end=' ')
    elif order[i] == 'B':
        print(B, end=' ')
    else:
        print(C, end=' ')