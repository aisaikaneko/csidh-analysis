from sage.all import *
from datetime import datetime
from time import time
import json

import sys
sys.path.append("..")
from csidh import *

data = {"trials": {}}
start_N = 5
end_N = 20
num_trials = (end_N - start_N) + 1

# Test the algorithm for 5-20 minimum primes
def test_program():
    for i in range(start_N, end_N+1):
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
        data["trials"][i] = {"A": int(A), "B": int(B), "A_priv": A_priv, "B_priv": B_priv, "A_shared": int(alice_shared), "B_shared": int(bob_shared), "result": alice_shared == bob_shared}

# Save the data and proof of the correct result in a file
def save_data(data, now):
    output = "basic_test_results_" + str(now) + ".json"
    path = "../Results/basic_test/" + output
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    now=datetime.now()
    start_time = time()
    test_program()
    end_time = time()
    data["time_taken"] = (end_time - start_time)
    data["num_trials"] = num_trials
    data["first_n"] = start_N
    data["last_n"] = end_N
    save_data(data, now)
