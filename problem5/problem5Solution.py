def matmul(A, B):
    n = len(A)
    m = len(B[0])
    k = len(B)
    C = [[0.0]*m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            s = 0.0
            for t in range(k):
                s += A[i][t] * B[t][j]
            C[i][j] = s
    return C

def matpow(P, power):
    # identity
    n = len(P)
    R = [[0.0]*n for _ in range(n)]
    for i in range(n):
        R[i][i] = 1.0

    base = P
    e = power
    while e > 0:
        if e % 2 == 1:
            R = matmul(R, base)
        base = matmul(base, base)
        e //= 2
    return R

P = [
    [0.8, 0.2, 0.0],  # Ready -> (Ready, Running, Blocked)
    [0.1, 0.1, 0.8],  # Running -> ...
    [0.2, 0.0, 0.8]   # Blocked -> ...
]

P2 = matpow(P, 2)
P7 = matpow(P, 7)

print("P^2[Ready][Running] =", P2[0][1])
print("P^7[Ready][Running] =", P7[0][1])

# Stationary distribution closed-form from solving pi = pi P:
pi_ready = 9/19
pi_running = 2/19
pi_blocked = 8/19
print("Stationary pi =", [pi_ready, pi_running, pi_blocked])