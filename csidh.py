from sage.all import *
import random as rand

# Converts a curve of the form y^2 = x^3 + Ax^2 + x to Weierstrauss form
def convert_to_weierstrauss(A):
    a = (3 - A**2) * pow(3 * 1, -1, p)
    b = (2 * A**3 - 9*A) * pow(27 * 1, -1, p)
    return EllipticCurve(F, [a, b])

# Converts a curve from Weierstrauss form back to the form y^2 + x^3 + Ax^2 + x
def convert_from_weierstrauss(E):
    a = E.a4()
    b = E.a6()
    R = PolynomialRing(F, name="z")
    roots = (z**3 + z*z + b).roots()
    r = roots[0][0]
    s = (3*s**2 + a).sqrt() ** (-1)
    return -3 * (-1)**s.is_square() * r * s

# Generate the parameters l_primes, p, and F_p for the key exchange
def gen_params(n):
    l_primes = primes_first_n(n + 1)[1:]
    p = 4 * prod(l_primes) - 1
    while not is_prime(p):
        x = next_prime(l_primes[-1] + 1)
        l_primes.append(x)
        p = (p + 1) * x - 1

    F = GF(p)
    return l_primes, p, F

# Generate the private and public keys for the key exchange
def gen_key(self, curve, m):
    return {
        "private": [random.randint(-m, m) for _ in range(self.n)],
        "public": curve
    }

# Apply the class group action on the curve
def group_action(key):
    e_list = key["private"]
    A = key["public"]
    E = get_curve(A)

