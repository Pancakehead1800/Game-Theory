
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

    cnts = [1]

    # Iterate through the days until everyone knows
    days = 0
    while not np.all(gnomes):
        cnts.append(gnomes.sum())
        days += 1

        # # Everyone chooses someone to contact
        choices = rng.integers(low=0, high=N, size=N)

        # # People who know the rumor will spread it to the perosn they contact
        gnomes[choices[gnomes == True]] = True

    cnts.append(gnomes.sum())
    return days, np.array(cnts)


# ============ GRAPHING ============ # 
def graph_days(days): 
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

def graph_cnts(cnts_lists):
    # Find longest simulation
    max_len = max(len(cnts) for cnts in cnts_lists)

    # Create a matrix filled with NaN
    cnts_matrix = np.full((len(cnts_lists), max_len), np.nan)

    # Put each simulation into one row
    for i, cnts in enumerate(cnts_lists):
        cnts_matrix[i, :len(cnts)] = cnts

    # Average across simulations
    average_cnts = np.nanmean(cnts_matrix, axis=0)

    # Plot
    plt.figure(figsize=(9, 5))
    plt.plot(average_cnts, marker="o", label="Average")
    plt.title("Average Rumor Spread")
    plt.xlabel("Day")
    plt.ylabel("Number of People Who Know the Rumor")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


# ============ EXECUTION ============ # 
if __name__ == "__main__":

    # Values of choice
    trials = 10_000
    N = 1000

    # Run the simulations
    results = [simulate_rumor(N=N) for _ in range(trials)]

    days = np.array([result[0] for result in results])
    cnts = [result[1] for result in results]

    graph_days(days)
    graph_cnts(cnts)

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
