from sage.all import *
from csidh import *

def setup_csidh(n, A, m):
    p, l_primes, F, E0 = gen_params(n, A)
    parameters = [p, l_primes, F, E0]
    n = len(l_primes)
    
    key_pair = gen_key(n, A, m)
    return (parameters, key_pair)
