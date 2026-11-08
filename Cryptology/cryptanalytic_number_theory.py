
from utils.number_theory import gcd, generate_primes, exp, totient, inv, solve_linear_congruence
import math

# Pollard's Rho method for finding small factors of a composite n
# Note: probabilistic algorithm; not deterministic
def factoring_pollard_rho(n, max_iterations=10000, seed=2, c=2):

    def f(x):
        return (x * x + c) % n

    x = f(seed)
    y = f(f(seed))

    for _ in range(max_iterations):
        g = gcd(abs(x - y), n)
        if 1 < g < n:
            return g
        if g == 1:
            x = f(x)
            y = f(f(y))
        if g == n:
            return None


def factoring_pollard_p_minus_1(n, B=100, b=2):
    primes = generate_primes(B)

    def floor_log(p, n):
        cnt = 0
        while n >= p:
            p *= p
            cnt += 1
        return cnt

    g = gcd(b, n)
    if g >= 2:
        return g

    for p in primes:
        l = floor_log(p, n)
        b = exp(b, exp(p, l, n), n)
        g = gcd(b - 1, n)
        if 1 < g < n:
            return g
        elif g == n:
            return None

    return None


def discrete_log_baby_step_giant_step(a, base, p):
    n = totient(p)
    m = math.floor(math.sqrt(n))
    lookup = {exp(base, j, p): j for j in range(m)}
    for i in range(m):
        ai = (a * inv(exp(base, m * i, p), p)) % p if i != 0 else a
        if ai in lookup:
            return (m * i + lookup[ai]) % n

    
def discrete_log_pollard_rho(a, base, p, max_iterations=10, seed=1):

    def f(z, z_m, z_n):
        if z % 3 == 0:
            return (z * base) % p, z_m, z_n+1
        elif z % 3 == 1:
            return (z * a) % p, z_m+1, z_n
        elif z % 3 == 2:
            return (z * z) % p, z_m*2, z_n*2

    t_p = totient(p)

    x, m_x, n_x = 1, 0, 0
    y, m_y, n_y = 1, 0, 0

    for _ in range(1, max_iterations):
        y1, m_y1, n_y1 = f(y, m_y, n_y)
        y, m_y, n_y = f(y1, m_y1, n_y1)
        x, m_x, n_x = f(x, m_x, n_x)

        if x == y:
            s = (m_x - m_y)
            t = (n_y - n_x)
            l = solve_linear_congruence(s, t, t_p)
            return l




# TESTING TESTNIG TESTING
if __name__ == "__main__":

    # pollard's rho factoring
    print(factoring_pollard_rho(35))
    print(factoring_pollard_rho(1843))

    # pollard's p-1 factoring
    print(factoring_pollard_p_minus_1(49, B=3, b=2))
    print(factoring_pollard_p_minus_1(9991, B=100, b=3))

    # baby-step giant-step discrete log
    print(discrete_log_baby_step_giant_step(3, 2, 29))
    print(discrete_log_baby_step_giant_step(3, 2, 101))

    # pollard's rho discrete log
    print(discrete_log_pollard_rho(9, 4, 59))

