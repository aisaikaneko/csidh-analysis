"""
csidh_key_time_correlation.py

For each implementation (CSIDH and CSIDH_CT) and for key sizes n = 5..20,
this script runs 100 iterations. For each iteration it records:
  - The time to compute the group action (shared secret derivation)
  - The magnitude of the private key (L1 norm)
  - The full details of the keys (both a_key and b_key)
  - The resulting secret (i.e. the output of the group action)
  - The protocol parameters (p and the list of small primes)

Then it performs a linear regression of time versus key magnitude,
plots the scatter with the regression line (annotated with r^2),
and saves all the detailed measurement data and regression results as a JSON file
in the Results folder.
"""

import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from time import perf_counter
from scipy.stats import linregress
sys.path.append("..")
from csidh import CSIDH
from csidh_ct import CSIDH_CT


# Get the L1 norm of the private key vector for linear regression later
def key_magnitude(private_key_vector):
    return sum(abs(x) for x in private_key_vector)


# Run tests for csidh or csidh_ct depending on the value of impl_class
def run_tests(impl_class, n_values, iterations, label):
    measurements = []
    print(f"Running tests for {label}")
    for n in n_values:
        print(f"  Testing key size n = {n}")
        for it in range(iterations):
            # Instantiate the implementation; this generates the parameters and keys
            instance = impl_class(n)
            
            # Save parameters: p and l_primes
            p_val = instance.p
            l_primes_val = instance.l_primes
            
            # Save the keys, converting public values to string in case they are Sage objects
            a_key = {
                "private": instance.a_key["private"],
                "public": str(instance.a_key["public"])
            }
            b_key = {
                "private": instance.b_key["private"],
                "public": str(instance.b_key["public"])
            }
            
            # Prepare the test input: using a_key's private part and b_key's public part
            test_input = {"public": instance.b_key["public"],
                          "private": instance.a_key["private"]}
            
            # Time the group action (shared secret derivation)
            start = perf_counter()
            secret = instance.group_action(test_input)
            end = perf_counter()
            elapsed = end - start
            
            # Compute key magnitude (L1 norm)
            kmag = key_magnitude(instance.a_key["private"])
            
            # Record all relevant information
            measurement = {
                "n": n,
                "iteration": it,
                "time": elapsed,
                "key_magnitude": kmag,
                "a_key": a_key,
                "b_key": b_key,
                "secret": str(secret),
                "parameters": {
                    "p": p_val,
                    "l_primes": l_primes_val
                }
            }
            measurements.append(measurement)
    return measurements


# Perform linear regression on the measurements from the tests
def perform_regression(measurements):
    x = np.array([m["key_magnitude"] for m in measurements])
    y = np.array([m["time"] for m in measurements])
    reg_result = linregress(x, y)
    r_squared = reg_result.rvalue ** 2
    return {
        "slope": reg_result.slope,
        "intercept": reg_result.intercept,
        "r_value": reg_result.rvalue,
        "p_value": reg_result.pvalue,
        "std_err": reg_result.stderr,
        "r_squared": r_squared
    }


# Create a scatter plot of key magnitude versus time, overlay the regerssion line, and annotate with r^2 value
def plot_results(measurements, regression_data, label, save_filename):
    x = np.array([m["key_magnitude"] for m in measurements])
    y = np.array([m["time"] for m in measurements])
    
    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, alpha=0.6, label="Data points")
    
    # Create regression line.
    x_line = np.linspace(x.min(), x.max(), 200)
    y_line = regression_data["slope"] * x_line + regression_data["intercept"]
    plt.plot(x_line, y_line, color="red",
             label=f"Regression line (r\u00b2 = {regression_data['r_squared']:.4f})")
    
    plt.xlabel("Key Magnitude (L1 norm)")
    plt.ylabel("Time for group action (s)")
    plt.title(f"{label}: Time vs. Key Magnitude")
    plt.legend()
    plt.grid(True)
    plt.savefig(save_filename)
    plt.show()


def main():
    # Ensure the Results folder exists
    results_dir = "Results"
    os.makedirs(results_dir, exist_ok=True)
    
    # Define the range of key sizes and the number of iterations per size
    n_values = list(range(5, 21))
    iterations = 100
    
    # Run tests for the non–constant-time implementation (csidh)
    csidh_measurements = run_tests(CSIDH, n_values, iterations, label="CSIDH")
    csidh_regression = perform_regression(csidh_measurements)
    print("CSIDH regression results:")
    print(csidh_regression)
    csidh_plot_file = os.path.join(results_dir, "csidh_time_vs_keymag.png")
    plot_results(csidh_measurements, csidh_regression,
                 label="CSIDH", save_filename=csidh_plot_file)
    
    # Run tests for the constant-time implementation (csidh_ct)
    csidh_ct_measurements = run_tests(CSIDH_CT, n_values, iterations, label="CSIDH_CT")
    csidh_ct_regression = perform_regression(csidh_ct_measurements)
    print("CSIDH_CT regression results:")
    print(csidh_ct_regression)
    csidh_ct_plot_file = os.path.join(results_dir, "csidh_ct_time_vs_keymag.png")
    plot_results(csidh_ct_measurements, csidh_ct_regression,
                 label="CSIDH_CT", save_filename=csidh_ct_plot_file)
    
    # Save all measurement data and regression results to a JSON file in the Results folder
    all_data = {
        "CSIDH": {
            "measurements": csidh_measurements,
            "regression": csidh_regression
        },
        "CSIDH_CT": {
            "measurements": csidh_ct_measurements,
            "regression": csidh_ct_regression
        }
    }
    json_file = os.path.join(results_dir, "csidh_key_time_correlation_data.json")
    with open(json_file, "w") as f:
        json.dump(all_data, f, indent=4)
    print(f"Results saved to {json_file}")


if __name__ == "__main__":
    main()

