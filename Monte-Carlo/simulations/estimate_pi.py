
from monte_carlo import MonteCarlo
import numpy as np


def estimate_pi(n=1000):
    # Generate a numpy array (n rows, 2 columns) of random points
    # Each coordinate is generated from the interval [0, 1) uniformly
    points = np.random.rand(n, 2)

    # Calculate the distance of each point from the origin
    distance = np.linalg.norm(points, axis=1)

    # Count the number of points with distance <= 1 from the origin
    inside_points = (distance <= 1).sum()

    # Determine the ratio of points inside the circle to total points
    ratio = inside_points / n

    # The ratio of the area of the circle (r=1) to the area of the square
    # (with corners at (-1,-1) and (1,1)) is pi/4
    # Thus, ratio = pi / 4 -> pi = 4 * ratio
    return 4 * ratio

if __name__ == "__main__":
    mc = MonteCarlo(estimate_pi, n=10000, trials=10000, label="π")
    mc.plot_results()
