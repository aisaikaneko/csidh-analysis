from sage.all import *

def verify_supersing(curve, field):
    # randomly pick point P in E(F_p) and set d = 1
    # for each l_i in l_primes do, run:
    #   Q_i = [(p+1)/l_i] * P
    #   [l_i]*Q == infty --> return 0 (ordinary)
    #   Q_i != inft --> d = l_i * d
    #   d > 4*sqrt(p) --> return 1 (supersingular)
