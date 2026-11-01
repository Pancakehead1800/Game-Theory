
import math


# find units of Z/n
def units_of_field(n):
    units = []
    for x in range(n):
        if gcd(x, n) == 1:
            units.append(x)
    return units


# find GCD of n, m
def gcd(n, m):
    # Edge cases
    if n < m:
        return gcd(m, n)
    if n == m:
        return n

    # Base case
    if m == 0:
        return n

    # Recursion case
    next_m = n % m
    next_n = m
    return gcd(next_n, next_m)


# find lcm of n, m
def lcm(n, m):
    # note: lcm(m, n) * gcd(m, n) = m * n
    return (m * n) // gcd(n, m)



# find multiplicative inverse of a mod m
def inv(a, m):
    if gcd(a, m) != 1:
        raise ValueError(f"a={a} has no modular inverse modulo m={m}")
    r0, r1 = a, m # remainders
    s0, s1 = 1, 0 # coefficients

    while r1 != 0:
        quotient = r0 // r1
        r0, r1 = r1, r0 - quotient * r1
        s0, s1 = s1, s0 - quotient * s1

    return s0 % m


# exponetiation algorithm
def exp(x, n, mod=None):
    res = 1

    if mod is None:
        powers = [x]
        while n > 0:
            prev = powers[-1]
            if n & 1: res *= prev
            n >>= 1
            powers.append(prev * prev)

    elif mod is not None:
        powers = [x % mod]
        while n > 0:
            prev = powers[-1]
            if n & 1: res = (res * prev) % mod
            n >>= 1
            powers.append((prev * prev) % mod)

    return res

# find the factors of n
def get_all_factors(n):
    factors = []
    for i in range(2, math.isqrt(n) + 1):
        if n % i == 0:
            factors.append(i)
            if i != n // i:
                factors.append(n // i)
    factors.sort()
    return factors


# find exponent of prime factor p of n
def exponent_of_factor(n: int, p: int) -> tuple[int, int]:
    res = 0
    while n % p == 0:
        n //= p
        res += 1
    return res, n


# Apply Euler's Criterion
def is_quadratic_residue(y, p):
    if p == 2:
        raise ValueError("Cannot use Euler's Criterion for p=2")

    power = (p - 1) // 2
    value = exp(y, power, p)

    if value == 1:
        return True
    elif value == p-1:
        return False
    else:
        raise ValueError("This function was probably implemented poorly...")

# Find principal square roots
def principal_sqrt(y, p):

    # first, check if we have easy case where p = 3 mod 4
    if p % 4 == 3:
        power = (p + 1) // 4
        x = exp(y, power, p)
        return x

    # 1. find s and m
    s, m = exponent_of_factor(p-1, 2)

    # 2. find a non-square g
    g = 2
    while is_quadratic_residue(g, p):
        g += 1

    # 3. iteration
    E = 0
    for i in range(2, s+1):
        pre1 = exp(g, E, p)       # g^E
        pre2 = (y * pre1) % p     # y * g^E 
        pre3 = exp(2, s-i, p)     # 2^(s-i)
        pre4 = m * pre3           # m * 2^(s-i)
        val  = exp(pre2, pre4, p) # (y * g^E)^(m * 2^(s-i))

        if val % p != 1:
            E += exp(2, i-1)

    # assume that h = y * g^E is in H = {1, a^(2^s), a^(2*2^s), ..., a^((m-1)2^s)}... hehe... what?
    h = (y * exp(g, E, p)) % p
    y = (h * exp(g, p-1-E))
    x = (exp(h, (m+1)//2, p) * exp(g, (p-1-E)//2, p)) % p

    return x, p-x


def nth_root(y, n, p):

    # easy case 1
    if gcd(n, p-1) == 1:
        r = inv(n, p-1)
        x = pow(y, r, p)
        return x

    # easy case 2
    if p % n == 1 and gcd(n, (p-1) // n):
        r = inv(n, (p-1) // n)
        x = exp(y, r, p)
        if exp(x, n, p) == y:
            return x

    print("Too difficult")


def totient(n):
    pass

def is_primitive_root(g, n):
    pwrs = [1]
    for i in range(1, n-1):
        pwrs.append((pwrs[-1] * g) % n)

    units = units_of_field(n)
    return len(set(pwrs)) == len(units)



def discrete_log(l, x, g, n):
    return True if exp(g, l, n) == x % n else False
    





# TESTING TESTING TESTING

# 2^57 mod 59:
print(exp(2, 57, 59))

# principal sqrt of 3 mod 107
print(principal_sqrt(3, 107))

# principal sqrt of 331 mod 449
print(principal_sqrt(331, 449))

# gcd(289572, 92848)
print(gcd(289572, 92848))

# multiplicative inverse to 19 mod 24
print(inv(19, 24))

# nth roots
print(nth_root(14, 3, 103))
print(nth_root(2, 3, 101))
print(nth_root(3, 7, 11))

# sqrt of 2 mod 17
print(principal_sqrt(2, 17))

# 3 primitive generator of Z/7?
print(units_of_field(7))
print(is_primitive_root(3, 7))
