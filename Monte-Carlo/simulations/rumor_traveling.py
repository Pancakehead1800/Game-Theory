
# ============ IMPORTS ============ #
import numpy as np
import matplotlib.pyplot as plt


# ============ SIMULATION ============ #
def simulate_rumor(N: int = 100):
    """
    Input:  int = the number of people present
    Output: int = the days it takes for the rumor to reach everyone
    """


    # The people who know the rumor
    gnomes = np.zeros(N, dtype=bool)
    gnomes[0] = True

    # Random number generator
    rng = np.random.default_rng()

    # Iterate through the days until everyone knows
    days = 0
    while not np.all(gnomes):
        days += 1

        # Everyone chooses someone to contact
        choices = rng.integers(low=0, high=N, size=N)

        # People who know the rumor will spread it to the perosn they contact
        gnomes[choices[gnomes == 1]] = True

    return days


# ============ GRAPHING ============ # 
def graph_results(days): 
    """Graph the distribution of the number of days.""" 
    plt.figure(figsize=(9, 5)) 
    plt.hist( days, bins=np.arange(days.min() - 0.5, days.max() + 1.5, 1), edgecolor="black" ) 
    plt.axvline( days.mean(), linestyle="--", linewidth=2, label=f"Mean = {days.mean():.2f} days" ) 
    plt.title("Distribution of Days for Rumor to Spread") 
    plt.xlabel("Number of Days") 
    plt.ylabel("Number of Simulations") 
    plt.legend() 
    plt.tight_layout() 
    plt.show()


if __name__ == "__main__":

    # Values of choice
    trials = 10000
    N = 100

    # Run the simulations
    days = np.array([simulate_rumor(N=100) for _ in range(trials)])
    graph_results(days)

    # Get the Mean and Standard Deviation
    mean = days.mean()
    std_dev = days.std(ddof=1)

    # Printing
    print()
    print("=" * 36)
    print("     RUMER SPREADING SIMULATION")
    print("=" * 36)
    print(f"     Number of People: {N}")
    print(f"     Number of Trials: {trials}")
    print("=" * 36)
    print(f"     Mean number of Days:  {mean}")
    print(f"     Standard Deviation:   {std_dev:.4}")
    print("=" * 36)
    print()
