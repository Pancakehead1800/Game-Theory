
import numpy as np
import matplotlib.pyplot as plt

# General Monte Carlo Class
class MonteCarlo:
    def __init__(self, trial_function: callable, n: int=100, trials: int=100, label: str=None):
        # Number of samples per trial
        self.n = n

        # Number of trials
        self.trials = trials

        # The user must create and pass in a function to represent a single trial
        self.trial_function = trial_function

        # To store the results of all the trials
        self.estimates = None

        # The user can specify what the estimated value represents
        self.label = label


    # Simulate all the trials
    def simulate_trials(self):
        estimates = np.array([self.trial_function(self.n) for _ in range(self.trials)])

        # Store the result of the first trial
        if self.estimates == None:
            self.estimates = estimates

        return estimates


    # Plot the results with a line plot and a histogram
    def plot_results(self):
        estimates = (
            self.estimates
            if self.estimates is not None
            else self.simulate_trials()
        )

        # Statistics
        mean = estimates.mean()
        std = estimates.std(ddof=1) # ddof=1 for unbiased estimate

        # Styling
        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=(8, 6), dpi=120)
        fig.patch.set_facecolor("black")
        ax.set_facecolor("#161a22")

        # Histogram
        ax.hist(
            estimates,
            bins=40,
            color="#4cc9f0",
            alpha=0.75,
            edgecolor="none",
            linewidth=0
        )

        # Mean line
        ax.axvline(
            mean,
            color="#ff6b6b",
            linewidth=2.5,
            linestyle="-",
            label=f"Mean: {mean:.4f}"
        )

        # Statistics box
        statistics_text = (
            f"Mean\n"
            f"{mean:.4f}\n"
            f"Std. Dev.\n"
            f"{std:.4f}"
        )

        ax.text(
            0.97,
            0.95,
            statistics_text,
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=11,
            color="#F8F9FA",
            bbox=dict(
                boxstyle="round,pad=0.6",
                facecolor="#202631",
                edgecolor="#3A4352",
                alpha=0.95
            )
        )

        # Labels
        ax.set_xlabel(
            "Estimate",
            fontsize=12,
            color="#D9DEE7",
            labelpad=10
        )

        value_label = (
            f"Value of {self.label}"
            if self.label is not None
            else "Value"
        )

        ax.set_ylabel(
            value_label,
            fontsize=12,
            color="#D9DEE7",
            labelpad=10
        )

        # Title
        ax.set_title(
            f"Monte Carlo Estimation\n"
            f"$n={self.n:,}$  •  {self.trials:,} trials",
            fontsize=17,
            fontweight="bold",
            color="#FFFFFF",
            pad=18
        )

        # Grid
        ax.grid(
            axis="y",
            color="#3A4352",
            linestyle="-",
            linewidth=0.7,
            alpha=0.35
        )

        # Remove unnecessary borders
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#3A4352")
        ax.spines["bottom"].set_color("#3A4352")

        # Ticks
        ax.tick_params(
            colors="#AAB2BF",
            labelsize=10
        )

        # Legend
        ax.legend(
            loc="upper left",
            frameon=False,
            fontsize=10
        )

        plt.tight_layout()
        plt.show()