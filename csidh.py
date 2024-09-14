from sage.all import *
import random as rand

class CSIDH():
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
        l_primes = self.l_primes
        
        # Return the base curve if each e_i = 0
        if all(e == 0 for e in e_list):
            return A

        # Apply the ideal corresponding to each prime l_i and exponent e_i
        while True:
            if all(e == 0 for e in e_list):
                break
            x = F.random_element()
            while x.is_zero():
                x = F.random_element()
            r = F(x**3 + A*x**2 + x)
            s = kronecker_symbol(r, p)
            assert (2 * is_square(r)) - 1 == s
            S = [i for i, e in enumerate(e_list) if sign(e) == s]
            if len(S) == 0:
                continue
            if s == -1:
                E = E.quadratic_twist()
            while True:
                y = E.random_element()
                if not y.is_zero():
                    break
            x = y.xy()[0]
            k = prod(l_primes[i] for i in S)
            P = E.lift_x(x)
            assert (p + 1) % k == 0
            Q = ((p + 1) // k) * P
            for i in S:
                assert k % l_primes[i] == 0
                R = (k // l_primes[i]) * Q
                if R.is_zero():
                    continue
                phi = E.isogeny(R)
                E = phi.codomain()
                Q = phi(Q)
                assert k % l_primes[i] == 0
                k = k // l_primes[i]
                e_list[i] -= s
            if s == -1:
                E = E.quadratic_twist()
        return self.convert_from_weierstrauss(E)

# Test the algorithm
def test_program():
    for i in range(5, 100):
        csidh = CSIDH(i)
        print(csidh.a_key)
        print(csidh.b_key)
        A = csidh.a_key["public"]
        B = csidh.b_key["public"]
        A_priv = csidh.a_key["private"]
        B_priv = csidh.b_key["private"]
        alice_shared = csidh.group_action({"public":B, "private":A_priv})
        bob_shared = csidh.group_action({"public":A, "private":B_priv})
        print(alice_shared)
        print(bob_shared)
        assert alice_shared == bob_shared
