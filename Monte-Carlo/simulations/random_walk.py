
from monte_carlo import MonteCarlo

import numpy as np
import matplotlib.pyplot as plt


class AdvancedMonteCarlo(MonteCarlo):
    def __init__(self, trial_function: callable, n: int=100, trials: int=100, label: str=None):
        super().__init__(trial_function, n, trials, label)
        self.walks = None
        self.estimates = None

    def simulate_walks(self):
        # Shape of walks is (trials, n, steps)
        walks = np.array([
            self.trial_function(n=self.n) for _ in range(self.trials)
        ])
        self.walks = walks

        # Shape of final position of each trial is (trials, n)
        # Shape of average final position for each trils is (trials,)
        estimates = walks[:, :, -1].mean(axis=1)
        self.estimates = estimates

        return estimates


    def plot_walks(self):
        if self.walks is None:
            self.simulate_walks()

        plt.style.use("dark_background")

        fig, ax = plt.subplots(figsize=(8, 6), dpi=120)

        fig.patch.set_facecolor("black")
        ax.set_facecolor("#161a22")

        ax.plot(self.walks[0].T, alpha=0.15)

        ax.set_title("Random Walks")
        ax.set_xlabel("Step")
        ax.set_ylabel("Position")

        plt.tight_layout()
        plt.show()

def random_walk(n=1000, steps=100):

    initial_value = 0.0
    increments = np.tanh(
        np.random.normal(
            loc=0.0,
            scale=1.0,
            size=(n, steps)
        )
    )
    samples = initial_value + np.cumsum(increments, axis=1)
    return samples


if __name__ == "__main__":
    amc = AdvancedMonteCarlo(trial_function=random_walk, n=1000, trials=1000)
    amc.plot_walks()

    