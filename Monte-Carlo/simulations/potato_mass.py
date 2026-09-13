
from monte_carlo import MonteCarlo
import numpy as np

# Diameter and length of fixed ellipsoid potato (cm)
DIAMETER = 2
LENGTH = 4

# Density of potatoes 
MEAN = 1.087
STD = 0.010

def estimate_potato_mass(n=1000, mean=MEAN, std=STD):
    # Acquire masses of potato
    masses = np.random.normal(loc=mean, scale=std, size=n)

    # Compute volume of the ellipsoid potatoes
    volume = (np.pi / 3) * 4 * (DIAMETER / 2) * (DIAMETER / 2) * (LENGTH / 2)

    # Scale masses by the fixed volume
    samples = masses * volume

    # Return the mean of each sample
    return np.mean(samples)

if __name__ == "__main__":
    mc = MonteCarlo(trial_function=estimate_potato_mass, n=1000, trials=10000)
    mc.plot_results()
