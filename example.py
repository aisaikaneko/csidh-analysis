from sage.all import *
import random as rand

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

# Converts a curve of the form y^2 = x^3 + Ax^2 + x to Weierstrauss form
def convert_to_weierstrauss(A):
    a = (3 - A**2) * pow(3 * 1, -1, p)
    b = (2 * A**3 - 9*A) * pow(27 * 1, -1, p)
    return EllipticCurve(F, [a, b])

# Converts a curve from Weierstrauss form back to the form y^2 + x^3 + Ax^2 + x
def convert_from_weierstrauss(E):
    a = E.a4()
    b = E.a6()
    F = E.base_field()
    R = PolynomialRing(F, name="z")
    z = R.gens()[0]
    roots = (z**3 + a*z + b).roots()
    assert len(roots) > 0
    r = roots[0][0]
    s = (3*r**2 + a).sqrt() ** (-1)
    return -3 * (-1)**s.is_square() * r * s

# Generate the private and public keys for the key exchange
def gen_key(self, curve, m):
    return {
        "private": [random.randint(-m, m) for _ in range(self.n)],
        "public": curve
    }

# Apply the class group action on the curve
def group_action(key):
    e_list = key["private"].copy()
    A = key["public"]
    E = convert_to_weierstrauss(A)
    
    if not (all*e == 0 for e in e_list):
        S = []
        while S == []:
            x = F.random_element()
            r = F(x**3 + A*x**2 + x)
            s = kronecker_symbol(r, p)
            for i in range(len(e_list)):
                if sign(e_list[i]) == s:
                    S.append(i)
        if s == -1:
            E = E.quadratic_twist()

        x = E.random_element()
        while x.is_zero():
            x = E.random_element()
        x = x.xy()[0]
        k = prod([l_primes[i] for i in S])
        P = E.lift_x(x)
        Q = ((p+1)//k) * P
        for i in S:
            R = (k // l_primes[i]) * Q
            if R.is_zero():
                continue
            phi = E.isogeny(R)
            E = phi.codomain()
            Q = phi(Q)
            k = k // l_primes[i]
            e_list[i] -= s
        if s == -1:
            E = E.quadratic_twist()
    return convert_from_weierstrauss(E)

l_primes, p, F = gen_params(3)
for _ in range(100):
    l_primes, p, F = gen_params(3)
    alice_priv = [randrange(-5, 6) for _ in range(len(l_primes))]
    bob_priv = [randrange(-5, 6) for _ in range(len(l_primes))]
    alice_pub = group_action({"public": 0, "private": alice_priv})
    bob_pub = group_action({"public": 0, "private": bob_priv})
    alice_shared = group_action({"public": bob_pub, "private": alice_priv})
    bob_shared = group_action({"public": alice_pub, "private": bob_priv})
    print(alice_shared)
    print(bob_shared)
    print(alice_shared == bob_shared)


