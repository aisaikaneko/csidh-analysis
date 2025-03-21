from sage.all import *
from time import time
import sys
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np

# Ensure the parent directory is in the path to import modules
sys.path.append("..")
from csidh import CSIDH
from csidh_ct import CSIDH_CT

# Set up file saving
import os
import json

results_dir = "../Results"
if not os.path.exists(results_dir):
    os.makedirs(results_dir)


# Set the outer loop counter up for later
i = 0


def run_experiment(Implementation, n_val, iterations=50):
    """
    Run the group action 50 times for a given implementation and N value.
    Returns:
        average_time: average time (in seconds) per group action call (averaging both Alice and Bob calls)
        times: list of individual average times per iteration.
    """
    times = []
    for n in range(iterations):
        cs = Implementation(n_val)
        # Extract public and private keys for both parties
        A = cs.a_key["public"]
        B = cs.b_key["public"]
        A_priv = cs.a_key["private"]
        B_priv = cs.b_key["private"]

        # Measure Alice's group action
        start_a = time()
        alice_shared = cs.group_action({"public": B, "private": A_priv})
        end_a = time()
        
        # Measure Bob's group action
        start_b = time()
        bob_shared = cs.group_action({"public": A, "private": B_priv})
        end_b = time()
        
        # Check that both shared secrets match
        if alice_shared != bob_shared:
            raise ValueError("Mismatch in shared secrets for N = {}.".format(n_val))
        
        # Average the time of the two group actions for this iteration
        avg_iteration_time = ((end_a - start_a) + (end_b - start_b)) / 2.0
        times.append(avg_iteration_time)

    average_time = sum(times) / len(times)
    return average_time, times

def main():
    # List of N values (minimum number of primes)
    N_values = []
    for N in range(5, 101):
        if N % 5 == 0:
            N_values.append(N)
    print(N_values)
    iterations = 30

    # To store average times for each N for CSIDH and CSIDH_CT
    csidh_avg_times = []
    csidh_ct_avg_times = []
    
    # Optionally, store the detailed timings for further analysis
    csidh_results = {}
    csidh_ct_results = {}

    for n in N_values:
        print("Current value of N: " + str(n))
        # Run experiment for CSIDH
        avg_time, times = run_experiment(CSIDH, n, iterations)
        csidh_avg_times.append(avg_time)
        csidh_results[n] = times

        # Run experiment for CSIDH_CT
        avg_time_ct, times_ct = run_experiment(CSIDH_CT, n, iterations)
        csidh_ct_avg_times.append(avg_time_ct)
        csidh_ct_results[n] = times_ct

        print(f"N = {n}: CSIDH average time = {avg_time:.6f} s, CSIDH_CT average time = {avg_time_ct:.6f} s")

    # Exponential model: y = a * exp(b * x)
    def exp_func(x, a, b):
        return a * np.exp(b * x)
    
    N_values_np = np.array(N_values)
    csidh_avg = np.array(csidh_avg_times)
    csidh_ct_avg = np.array(csidh_ct_avg_times)
    
    # Compute initial guess for CSIDH using a linear fit on log data
    csidh_lin_fit = np.polyfit(N_values_np, np.log(csidh_avg), 1)
    csidh_initial_guess = [np.exp(csidh_lin_fit[1]), csidh_lin_fit[0]]
    
    # Compute initial guess for CSIDH_CT similarly
    csidh_ct_lin_fit = np.polyfit(N_values_np, np.log(csidh_ct_avg), 1)
    csidh_ct_initial_guess = [np.exp(csidh_ct_lin_fit[1]), csidh_ct_lin_fit[0]]
    
    # Use the initial guesses in the curve_fit call
    csidh_params, _ = curve_fit(exp_func, N_values_np, csidh_avg, p0=csidh_initial_guess)
    csidh_ct_params, _ = curve_fit(exp_func, N_values_np, csidh_ct_avg, p0=csidh_ct_initial_guess)
    
    csidh_fit = exp_func(N_values_np, *csidh_params)
    csidh_ct_fit = exp_func(N_values_np, *csidh_ct_params)

    # Create a plot of the average times versus N for both implementations
    plt.figure()
    plt.plot(N_values, csidh_avg_times, marker='o', label="CSIDH")
    plt.plot(N_values, csidh_ct_avg_times, marker='s', label="CSIDH_CT")
    plt.plot(N_values, csidh_fit, '--', label=f'CSIDH exp fit: y = {csidh_params[0]:.3f} * exp({csidh_params[1]:.3f} * x)')
    plt.plot(N_values, csidh_ct_fit, '--', label=f'CSIDH_CT exp fit: y = {csidh_ct_params[0]:.3f} * exp({csidh_ct_params[1]:.3f} * x)')
    plt.xlabel("Minimum Number of Primes (N)")
    plt.ylabel("Average Group Action Time (seconds)")
    plt.title("Performance Comparison: CSIDH vs CSIDH_CT")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "performance_comparison.png"))
    plt.show()

    # Prepare the data to be saved in JSON format
    results_data = {
        "N_values": N_values,
        "CSIDH_avg_times": csidh_avg_times,
        "CSIDH_CT_avg_times": csidh_ct_avg_times,
        "CSIDH_individual_times": csidh_results,
        "CSIDH_CT_individual_times": csidh_ct_results
    }

    # Write the JSON file to the Results folder
    json_path = os.path.join(results_dir, "performance_data.json")
    with open(json_path, 'w') as json_file:
        json.dump(results_data, json_file, indent=4)
    
    print("Results saved in:", results_dir)

if __name__ == "__main__":
    main()

