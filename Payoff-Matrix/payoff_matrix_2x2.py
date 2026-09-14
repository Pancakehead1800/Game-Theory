

class PayoffMatrix2x2:
    def __init__(
        self, 
        payoff_matrix: list[list[list[float, float]]]=None,
        actions: list[str]=["Action 1A", "Action 1B", "Action 2A", "Action 2B"]
    ):
        # 2 x 2 payoff matrix
        # Rows are player 1, columns are player 2
        # The class uses matrix[row][col][player] for indexing
        self.payoff_matrix = payoff_matrix

        # Action labels
        # First 2 are for player 1, second 2 are for player 2
        self.actions = actions

        # Dominant Strategies
        self.p1_dominant = None
        self.p2_dominant = None

        # Nash Equilibria
        self.equilibria = None


    # Find Dominant Strategies for both players (if any)
    def find_dominant_strategies(self):
        # Goal is to maximize utility

        player_1_dominant: int = None
        player_2_dominant: int = None

        # -------- Player 1 --------
        # We must check if Action 1A has better/worse utility in both columns compared to Action 1B
        # Difference: (Action 1 Utility) - (Action 2 Utility)
        col_1_diff = self.payoff_matrix[0][0][0] - self.payoff_matrix[1][0][0]
        col_2_diff = self.payoff_matrix[0][1][0] - self.payoff_matrix[1][1][0]

        if col_1_diff > 0 and col_2_diff > 0:
            player_1_dominant = self.actions[0] # Action 1A
        elif col_1_diff < 0 and col_2_diff < 0:
            player_1_dominant = self.actions[1] # Action 1B
        else:
            player_1_dominant = None


        # -------- Player 2 --------
        # Same process, but with Player 2
        row_1_diff = self.payoff_matrix[0][0][1] - self.payoff_matrix[0][1][1]
        row_2_diff = self.payoff_matrix[1][0][1] - self.payoff_matrix[1][1][1]

        if row_1_diff > 0 and row_2_diff > 0:
            player_2_dominant = self.actions[2] # Action 2A
        elif row_1_diff < 0 and row_2_diff < 0:
            player_2_dominant = self.actions[3] # Action 2B
        else:
            player_2_dominant = None

        self.p1_dominant = player_1_dominant
        self.p2_dominant = player_2_dominant
        return (self.p1_dominant, self.p2_dominant)


    # Find all Nash Equilibria
    def find_nash_equilibria(self):
        equilibria = []
        # -------- Check Top-Left --------
        # Check Action 1B
        if self.payoff_matrix[1][0][0] > self.payoff_matrix[0][0][0]:
            # Check Action 2B
            if self.payoff_matrix[0][1][1] > self.payoff_matrix[0][0][1]:
                equilibria.append((self.actions[0], self.actions[2]))

        # --------Check Top-Right --------
        # Check Action 1B
        if self.payoff_matrix[1][1][0] > self.payoff_matrix[0][1][0]:
            # Check Action 2A
            if self.payoff_matrix[0][0][1] > self.payoff_matrix[0][1][1]:
                equilibria.append((self.actions[0], self.actions[3]))

        
        # --------Check Bottom-Left --------
        # Check Action 1A
        if self.payoff_matrix[0][0][0] > self.payoff_matrix[1][0][0]:
            # Check Action 2B
            if self.payoff_matrix[1][1][1] > self.payoff_matrix[1][0][1]:
                equilibria.append((self.actions[1], self.actions[2]))

 
        # --------Check Bottom-Right --------
        # Check Action 1A
        if self.payoff_matrix[0][1][0] > self.payoff_matrix[1][1][0]:
            # Check Action 2A
            if self.payoff_matrix[1][0][1] > self.payoff_matrix[1][1][1]:
                equilibria.append((self.actions[1], self.actions[3]))

        self.equilibria = equilibria
        return self.equilibria
    

    def print_summary(self):
        entry_length = max(
            [len(str(entry)) for row in self.payoff_matrix for entry in row] +
            [len(label) for label in self.actions] +
            [len("Action XX")]
        )

        # len(str(entry)) for row in self.payoff_matrix for entry in row)
        if self.actions is None:
            self.actions = ["Action 1A", "Action 2A", "Action 1B", "Action 2B"]

        seperator = "-" * (entry_length + 2)
        space = " " * (entry_length + 2)

        # format strings
        def fstr(s):
            if type(s) is not str:
                s = str(s)
            return s + " " * (entry_length - len(s))

        return (
            f"{"=" * (3 * (entry_length + 2) + 7)}\n"
            f"{"Payoff Matrix\n"}"
            f"{"=" * (3 * (entry_length + 2) + 7)}\n"
            f"{space}| {fstr(self.actions[2])} | {fstr(self.actions[3])} |\n"
            f"{seperator}|{seperator}|{seperator}\n"
            f" {fstr(self.actions[0])} | {fstr(self.payoff_matrix[0][0])} | {fstr(self.payoff_matrix[0][1])} |\n"
            f"{seperator}|{seperator}|{seperator}\n"
            f" {fstr(self.actions[1])} | {fstr(self.payoff_matrix[1][0])} | {fstr(self.payoff_matrix[1][1])} |\n"
            f"{"=" * (3 * (entry_length + 2) + 7)}\n"
            f"Player 1 Dominant Strategy: {self.p1_dominant}\n"
            f"Player 2 Dominant Strategy: {self.p2_dominant}\n"
            f"{"=" * (3 * (entry_length + 2) + 7)}\n"
            f"Nash Equilibria: {self.equilibria}\n"
            f"{"=" * (3 * (entry_length + 2) + 7)}\n"
        )

    def __repr__(self):
        return self.print_summary()


    # Get the payoff matrix from the user
    def get_payoff_matrix(self):
        if self.payoff_matrix is None:
            self.payoff_matrix = []
            for _ in range(2):
                self.payoff_matrix.append(list(map(float, input("Enter the row: ").split())))



if __name__ == "__main__":

    # Example matrix from a Prisoner's Dilemma situation
    test_matrix = [
        [[2, 2], [-1, 3]],
        [[3, -1], [0, 0]]
    ]

    pm = PayoffMatrix2x2(payoff_matrix=test_matrix)
    pm.find_dominant_strategies()
    pm.find_nash_equilibria()
    print(pm)
