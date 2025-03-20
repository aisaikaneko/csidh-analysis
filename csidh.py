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
            l_primes[-1] = x
            p = 4 * prod(l_primes) - 1

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
        A = key["public"]                           # Coefficient for elliptic curve
        E = self.convert_to_weierstrauss(A)
        p = self.p                                  # The prime to use for the group acton
        F = self.F                                  # Prime field with orer p
        l_primes = self.l_primes                    # List of small primes
        
        # Return the base curve if each e_i = 0
        if all(e == 0 for e in e_list):
            return A

        # Apply the ideal corresponding to each prime l_i and exponent e_i
        # Uses a loop structure to apply each idela the right number of times until no more exponents remain
        while True:
            # If no exponent is positive, then end and return E
            if all(e == 0 for e in e_list):
                break

            # Get a non-zero random element of F
            x = F.random_element()
            while x.is_zero():
                x = F.random_element()

            # Set s to the Kronecker symbol of r for p
            r = F(x**3 + A*x**2 + x)
            s = kronecker_symbol(r, p)
            assert (2 * is_square(r)) - 1 == s

            # Create a set of all non-zero indices
            S = [i for i, e in enumerate(e_list) if sign(e) == s]
            if len(S) == 0:
                continue
            if s == -1:
                E = E.quadratic_twist()
            
            # Get a random point on the curve and get the product of all elements
            while True:
                y = E.random_element()
                if not y.is_zero():
                    break
            x = y.xy()[0]
            k = prod(l_primes[i] for i in S)
            P = E.lift_x(x)

            # Ensure that p + 1 divides k and define Q = ((p + 1) / k) * P
            assert (p + 1) % k == 0
            Q = ((p + 1) // k) * P

            # Apply the isogeny corresponding to each l_prime power to compute E_B
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
