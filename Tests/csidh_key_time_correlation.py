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


# Makes a SageMath class serializable by converting it to a normal integer
def make_json_serializable(obj):
    if isinstance(obj, dict):
        return {make_json_serializable(k): make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(i) for i in obj]
    elif hasattr(obj, 'is_integer') and obj.is_integer():
        return int(obj)
    else:
        return obj


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


# Perform linear regression on the measurements for each individual n
def perform_regression_per_n(measurements):
    measurements_by_n = {}
    for m in measurements:
        measurements_by_n.setdefault(m["n"], []).append(m)
    
    regressions = {}
    for n, group in measurements_by_n.items():
        x = np.array([m["key_magnitude"] for m in group])
        y = np.array([m["time"] for m in group])
        reg_result = linregress(x, y)
        regressions[n] = {
            "slope": reg_result.slope,
            "intercept": reg_result.intercept,
            "r_value": reg_result.rvalue,
            "p_value": reg_result.pvalue,
            "std_err": reg_result.stderr,
            "r_squared": reg_result.rvalue ** 2
        }
    return regressions


# Create a scatter plot of key magnitude versus time, overlay the regression line, and annotate with r^2 value
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
    plt.close()


def main():
    # Ensure the Results folder exists
    results_dir = "../Results/csidh_key_time_correlation"
    os.makedirs(results_dir, exist_ok=True)
    
    # Define the range of key sizes and the number of iterations per size
    n = int(input("Enter the highest value of n to test (starting at n = 5): "))
    n_values = list(range(5, n+1))
    iterations = 100
    
    # Run tests for the non–constant-time implementation (csidh)
    csidh_measurements = run_tests(CSIDH, n_values, iterations, label="CSIDH")
    csidh_regression = perform_regression(csidh_measurements)
    csidh_regression_per_n = perform_regression_per_n(csidh_measurements)
    print("CSIDH overall regression results:")
    print(csidh_regression)
    print("CSIDH regression results per n:")
    print(csidh_regression_per_n)
    csidh_plot_file = os.path.join(results_dir, "csidh_time_vs_keymag.png")
    plot_results(csidh_measurements, csidh_regression,
                 label="CSIDH", save_filename=csidh_plot_file)
    
    # Run tests for the constant-time implementation (csidh_ct)
    csidh_ct_measurements = run_tests(CSIDH_CT, n_values, iterations, label="CSIDH_CT")
    csidh_ct_regression = perform_regression(csidh_ct_measurements)
    csidh_ct_regression_per_n = perform_regression_per_n(csidh_ct_measurements)
    print("CSIDH_CT overall regression results:")
    print(csidh_ct_regression)
    print("CSIDH_CT regression results per n:")
    print(csidh_ct_regression_per_n)
    csidh_ct_plot_file = os.path.join(results_dir, "csidh_ct_time_vs_keymag.png")
    plot_results(csidh_ct_measurements, csidh_ct_regression,
                 label="CSIDH_CT", save_filename=csidh_ct_plot_file)
    
    # For each n, create and save a plot of the regression (key magnitude vs time) for that n, for both implementations.
    measurements_by_n_csidh = {}
    for m in csidh_measurements:
        measurements_by_n_csidh.setdefault(m["n"], []).append(m)
    measurements_by_n_csidh_ct = {}
    for m in csidh_ct_measurements:
        measurements_by_n_csidh_ct.setdefault(m["n"], []).append(m)
    
    for n in n_values:
        if n in measurements_by_n_csidh:
            reg = perform_regression(measurements_by_n_csidh[n])
            plot_file = os.path.join(results_dir, f"csidh_n_{n}_regression.png")
            plot_results(measurements_by_n_csidh[n], reg, f"CSIDH n={n}", plot_file)
        if n in measurements_by_n_csidh_ct:
            reg = perform_regression(measurements_by_n_csidh_ct[n])
            plot_file = os.path.join(results_dir, f"csidh_ct_n_{n}_regression.png")
            plot_results(measurements_by_n_csidh_ct[n], reg, f"CSIDH_CT n={n}", plot_file)
    
    # Create a linear approximation for n vs r^2, based on per-n regression data.
    csidh_n = []
    csidh_r2 = []
    for n in sorted(csidh_regression_per_n.keys()):
        csidh_n.append(n)
        csidh_r2.append(csidh_regression_per_n[n]["r_squared"])
    csidh_n = np.array(csidh_n)
    csidh_r2 = np.array(csidh_r2)
    csidh_lin = linregress(csidh_n, csidh_r2)
    csidh_r2_line = csidh_lin.slope * csidh_n + csidh_lin.intercept
    plt.figure(figsize=(8,6))
    plt.plot(csidh_n, csidh_r2, 'o', label="CSIDH r² values")
    plt.plot(csidh_n, csidh_r2_line, 'r--', label=f"CSIDH linear approx (slope={csidh_lin.slope:.4f})")
    csidh_r2_lin_plot = os.path.join(results_dir, "csidh_n_vs_r2.png")
    plt.savefig(csidh_r2_lin_plot)
    plt.close()
    
    csidh_ct_n = []
    csidh_ct_r2 = []
    for n in sorted(csidh_ct_regression_per_n.keys()):
        csidh_ct_n.append(n)
        csidh_ct_r2.append(csidh_ct_regression_per_n[n]["r_squared"])
    csidh_ct_n = np.array(csidh_ct_n)
    csidh_ct_r2 = np.array(csidh_ct_r2)
    csidh_ct_lin = linregress(csidh_ct_n, csidh_ct_r2)
    csidh_ct_r2_line = csidh_ct_lin.slope * csidh_ct_n + csidh_ct_lin.intercept
    plt.figure(figsize=(8,6))
    plt.plot(csidh_ct_n, csidh_ct_r2, 'o', label="CSIDH_CT r² values")
    plt.plot(csidh_ct_n, csidh_ct_r2_line, 'r--', label=f"CSIDH_CT linear approx (slope={csidh_ct_lin.slope:.4f})")
    csidh_ct_r2_lin_plot = os.path.join(results_dir, "csidh_ct_n_vs_r2.png")
    plt.savefig(csidh_ct_r2_lin_plot)
    plt.close()
    
    # Create and show a plot comparing the linear analyses of n vs r^2 for CSIDH and CSIDH_CT
    plt.figure(figsize=(8,6))
    plt.plot(csidh_n, csidh_r2, 'bo', label="CSIDH r²")
    plt.plot(csidh_n, csidh_r2_line, 'b--', label="CSIDH linear approx")
    plt.plot(csidh_ct_n, csidh_ct_r2, 'go', label="CSIDH_CT r²")
    plt.plot(csidh_ct_n, csidh_ct_r2_line, 'g--', label="CSIDH_CT linear approx")
    plt.xlabel("n (key size)")
    plt.ylabel("r² (correlation coefficient squared)")
    plt.title("Comparison of n vs. r² for CSIDH and CSIDH_CT")
    plt.legend()
    plt.grid(True)
    combined_plot = os.path.join(results_dir, "combined_n_vs_r2.png")
    plt.savefig(combined_plot)
    plt.show()
    
    # Save all measurement data and regression results to a JSON file in the Results folder
    all_data = {
        "CSIDH": {
            "measurements": csidh_measurements,
            "overall_regression": csidh_regression,
            "regression_per_n": csidh_regression_per_n,
            "n_vs_r2": {str(n): csidh_regression_per_n[n]["r_squared"] for n in csidh_regression_per_n}
        },
        "CSIDH_CT": {
            "measurements": csidh_ct_measurements,
            "overall_regression": csidh_ct_regression,
            "regression_per_n": csidh_ct_regression_per_n,
            "n_vs_r2": {str(n): csidh_ct_regression_per_n[n]["r_squared"] for n in csidh_ct_regression_per_n}
        }
    }
    json_file = os.path.join(results_dir, "csidh_key_time_correlation_data.json")
    with open(json_file, "w") as f:
        json.dump(make_json_serializable(all_data), f, indent=4)
    print(f"Results saved to {json_file}")


if __name__ == "__main__":
    main()

