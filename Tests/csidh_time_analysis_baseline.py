from sage.all import *
from time import time
import sys
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import json

sys.path.append("..")
from csidh import *

N = 100   # Number of trials to average per value of n

# Measure the time taken to derive the shared secret for various parameters
def get_time(n):
    csidh = CSIDH(n)
    start_time = time()
    secret = csidh.group_action({"public":csidh.b_key["public"], "private":csidh.a_key["private"]})
    end_time = time()
    print("Secret: " + str(secret))
    print("Time: " + str(end_time - start_time))
    return (end_time - start_time)

# Compute the average of the times for each n
def get_averages(n_times, save_file=None):
    n_vals = list(n_times.keys())
    n_avgs = {}
    for n in n_vals:
        n_avg = sum(n_times[n]) / len(n_times[n])
        n_avgs[n] = n_avg
    return n_avgs

# Plot the average time taken to derive the shared secret per value of n
def plot_averages(n_avgs, save_file=None):
    n_vals = list(n_avgs.keys())
    avg_times = list(n_avgs.values())

    plt.plot(n_vals, avg_times, marker='o')
    plt.xlabel('n')
    plt.ylabel('Average Time (s)')
    plt.title('Average Time to Derive Shared Secret with >=n Primes')
    plt.grid(True)
    if save_file:
        plt.savegif(save_file)
    plt.show()

# Fit the data to exponential and polynomial models to estimate the complexity
def estimate_complexity(n_avgs, save_file=None):
    n_vals = np.array(list(n_avgs.keys()))
    avg_times = np.array(list(n_avgs.values()))

    # Represent an exponential function
    def exp_func(x, a, b):
        return a * np.exp(b * x)

    # Represent a quadratic function
    def quad_func(x, a, b, c):
        return a*x**2 + b*x + c

    # Represent a cubic function
    def cubic_func(x, a, b, c, d):
        return a*x**3 + b*x**2 + c*x + d

    # Fit the data to different function models
    exp_params, _ = curve_fit(exp_func, n_vals, avg_times)
    quad_params, _ = curve_fit(quad_func, n_vals, avg_times)
    cubic_params, _ = curve_fit(cubic_func, n_vals, avg_times)
    exp_fit = exp_func(n_vals, *exp_params)
    quad_fit = quad_func(n_vals, *quad_params)
    cubic_fit = cubic_func(n_vals, *cubic_params)

    # Plot the original data and the functions
    plt.plot(n_vals, avg_times, 'o', label='Data')
    plt.plot(n_vals, exp_fit, '--', label=f'Exponential fit: y = {exp_params[0]:.3f} * exp({exp_params[1]:.3f} * x)')
    plt.plot(n_vals, quad_fit, '--', label=f'Quadratic fit: y = {quad_params[0]:.3f}x^2 + {quad_params[1]:.3f}x + {quad_params[2]:.3f}')
    plt.plot(n_vals, cubic_fit, '--', label=f'Cubic fit: y = {cubic_params[0]:.3f}x^3 + {cubic_params[1]:.3f}x^2 + {cubic_params[2]:.3f}x + {cubic_params[3]:.3f}')
    plt.xlabel('n')
    plt.ylabel('Average Time (s)')
    plt.legend()
    plt.title('Exponential vs Polynomial Fits')
    plt.grid(True)
    if save_file:
        plt.savefig(save_file)
    plt.show()

    # Log-transform the data to check if the growth is linear on a log scale
    log_avg_times = np.log(avg_times)
    plt.plot(n_vals, log_avg_times, 'o-', label='Log-transformed Data')
    plt.xlabel('n')
    plt.ylabel('log(Average Time)')
    plt.title('Log-transformed Data for Exponential Check')
    plt.grid(True)
    if save_file:
        log_save_file = save_file.replace('.png', '_log.png')
        plt.savefig(log_save_file)
    plt.show()

    return [exp_fit, quad_fit, cubic_fit]

# Save the results of the analysis
def save_data(data):
    output = "csidh_time_analysis_data.json"
    with open(output, 'w') as f:
        json.dump(data, f, indent=4)

# Run the test to measure the average time taken for each value of n and compare them
if __name__ == "__main__":
    n_vals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    n_times = {}
    n_avgs = {}
    for n in n_vals:
        n_times[n] = []
        for i in range(N):
            n_time = get_time(n)
            n_times[n].append(n_time)
        n_avgs = get_averages(n_times)

    # Plot the averages and time estimated complexity functions
    functions = estimate_complexity(n_avgs, save_file="average_time_plot.png")

    # Save the results of the analyses in a JSON file
    save_data({"n_times": n_times, "n_avgs": n_avgs, "exp_fit": functions[0].tolist(), "quad_fit": functions[1].tolist(), "cubic_fit": functions[2].tolist()})
