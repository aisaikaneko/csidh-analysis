from sage.all import *
import random as rand

class CSIDH():
    def __init__(n):
        self.l_primes, self.p, self.F = self.gen_params(n)
        self.a_key = self.gen_key(5)
        self.b_key = self.gen_key(5)

    # Generate the private and public keys for the key exchange
    def gen_key(self, m):
        private = [random.randint(-m, m) for _ in range(self.n)]
        public = self.group_action(0, private)
        return {
            "private": private,
            "public": public
        }

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

    # Apply the CSIDH group action to the curve

