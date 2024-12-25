from sage.all import *
import random as rand

class CSIDH_CT():
    def __init__(self, n):
        self.n = n
        self.l_primes, self.p, self.F = self.gen_params(n)
        self.a_key = self.gen_key(n)
        self.b_key = self.gen_key(n)

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
        private = [rand.randint(0, 2*m) for _ in range(self.n)]
        public = self.group_action({"public": 0, "private": private})
        return {
            "private": private,
            "public": public
        }

    # Converts a curve of the form y^2 = x^3 + Ax^2 + x to simplified Weierstrauss form
    def convert_to_weierstrauss(self, A):
        a = (3 - A**2) * pow(3 * 1, -1, self.p)
        b = (2 * A**3 - 9*A) * pow(27 * 1, -1, self.p)
        return EllipticCurve(self.F, [a, b])

    # Converts a curve from simplified Weierstrauss form back to A from the form y^2 = x^3 + Ax^2 + x
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
        e_list = key["private"].copy()              # List of exponents of prime ideals
        f_list = []                                 # List of dummy isogenies to compute for each degree
        for e in e_list:
            f_list.append(10 - e)
        A = key["public"]                           # Coefficient for elliptic curve
        E = self.convert_to_weierstrauss(A)
        p = self.p                                  # The prime to use for the group acton
        F = self.F                                  # Prime field with orer p
        l_primes = self.l_primes                    # List of small primes
        k = 4

        # Return the base curve if each e_i = 0
        while True:
            # Ensure that real and/or dummy isogenies still need to be applied
            if all(e == 0 for e in e_list) and all(f == 0 for f in f_list):
                break

            # Get a random point on the curve
            while True:
                y = E.random_element()
                if not y.is_zero():
                    break
            x = y.xy()[0]
            P = E.lift_x(x)
            P = k*P

            # Generate the set S of indices to compute as real or dummy isogenies
            S = []
            for i in range(len(e_list)):
                if e_list[i] != 0 or f_list[i] != 0:
                    S.append(i)

            # Compute the real and/or dummy isogenies for each i in S
            for i in S:
                m = 1
                for j in S:
                    if j > i:
                        m *= j
                K = m*P

                # Apply real and/or dummy isogenies in the same loop
                if not K.is_zero():
                    if e_list[i] != 0:
                        phi = E.isogeny(K)
                        E = phi.codomain()
                        P = phi(P)
                        e_list[i] -= 1
                    else:
                        P = l_primes[i]*P
                        f_list[i] -= 1
                    if e_list[i] == 0 and f_list[i] == 0:
                        k = k * l_primes[i]

        # Convert back from Weierstrauss form
        return self.convert_from_weierstrauss(E)
