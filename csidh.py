from sage.all import *
import random as rand

class CSIDH():
    def __init__(self, n):
        self.n = n
        self.l_primes, self.p, self.F = self.gen_params(n)
        self.a_key = self.gen_key(5)
        self.b_key = self.gen_key(5)

    # Generate the parameters l_primes, p, and F_p for the key exchange
    def gen_params(self, n):
        l_primes = primes_first_n(n + 1)[1:]
        p = 4 * prod(l_primes) - 1
        while not is_prime(p):
            x = next_prime(l_primes[-1] + 1)
            l_primes.append(x)
            p = (p + 1) * x - 1

        F = GF(p)
        return l_primes, p, F

    # Generate the private and public keys for the key exchange
    def gen_key(self, m):
        private = [rand.randint(-m, m) for _ in range(self.n)]
        public = self.group_action({"public": 0, "private": private})
        return {
            "private": private,
            "public": public
        }

    # Converts a curve of the form y^2 = x^3 + Ax^2 + x to Weierstrauss form
    def convert_to_weierstrauss(self, A):
        a = (3 - A**2) * pow(3 * 1, -1, self.p)
        b = (2 * A**3 - 9*A) * pow(27 * 1, -1, self.p)
        return EllipticCurve(self.F, [a, b])

    # Converts a curve from Weierstrauss form back to A from the form y^2 = x^3 + Ax^2 + x
    def convert_from_weierstrauss(self, E):
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

    # Apply the CSIDH group action
    def group_action(self, key):
        # Set up parameters
        e_list = key["private"].copy()
        A = key["public"]
        E = self.convert_to_weierstrauss(A)
        p = self.p
        F = self.F
        
        # Return the base curve if each e_i = 0
        if all(e == 0 for e in e_list):
            return A

        # Apply the ideal corresponding to each prime l_i and exponent e_i
        
