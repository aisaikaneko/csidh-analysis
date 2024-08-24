from sage.all import *

# Set the 
def run_csidh(n, A, B, m):
    p, l_primes, F, E0 = gen_params(n, A)
    parameters = [p, l_primes, F, E0]
    n = len(l_primes)
    
    a_key_pair = gen_key(n, A, m)
    b_key_pair = gen_key(n, B, m)

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

# Verify the supersingularity of the curve generated as a parameter.
# Returns 0 if ordinary and 1 if supersingular.
def verify_supersing(p, l_primes, F, E0):
    P = E0.random_point()
    d = 1

    for li in l_primes:
        Q = ((p + 1) // li) * P  # Note: use integer division here
        if li * Q == E0(0):
            return 0
        if Q != E0(0):
            d = li * d
            if d > 4 * (p**(1/2)):
                return 1
    return 0

# Perform the key exchange.
def derive_secret(pair, pub_key):
    pass
    

# Generate the private key to be used in the encryption.
def gen_key(n, A, m):
    return {"private":[randint(-m, m) for _ in range(n)], "public":A}
