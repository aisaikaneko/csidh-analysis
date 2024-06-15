# Generate the parameters for the protocol, including the n small primes, the prime p defining 
# Define the parameters of the protocol.
n = 5                                   # Number of "small primes" l_i to use to generate p.
A = 1                                   # The Montgomery coefficient of the base field.
p, l_primes, F, E0 = gen_params(n, A)   # Get the prime, small primes, field, and base curve. 
n = len(l_primes)                       # Update n after generating primes.
m = 5                                   # Range for the random integers of the private key.

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
def gen_key(n):
    return {"private":[randint(-5, 5) for _ in range(n)], "public":A}











