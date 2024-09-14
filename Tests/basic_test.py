from sage.all import *
import sys
sys.path.append("..")
from csidh import *

# Test the algorithm for 5-20 minimum primes
def test_program():
    for i in range(5, 20):
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

if __name__ == "__main__":
    test_program()
