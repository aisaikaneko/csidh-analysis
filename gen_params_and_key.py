from sage.all import *

# the field F, base curve E0, and small primes l_primes.
def gen_params(n, A):
    l_primes = primes_first_n(n+1)[1:]
    p = 4 * prod(l_primes) - 1
    while not is_prime(p):
        x = next_prime(l_primes[-1]+1)
        l_primes.append(x)
        p = (p + 1) * x - 1
    
    F = GF(p)
    E0 = EllipticCurve(F, [A, 0])

    return p, l_primes, F, E0

# Generate the private key to be used in the encryption.
def gen_key(n, A, m):
    return {"private":[randint(-m, m) for _ in range(n)], "public":A}
