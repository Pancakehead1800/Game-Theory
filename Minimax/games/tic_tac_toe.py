
# In an ideal game, there will be a Tie (or a 2.0 evaluation)
class State:
    def __init__(self, turn: str="X", grid=None):
        self.evaluation = None
        self.branches = None
        self.turn = turn
        self.grid = grid if grid is not None else [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]


    def __repr__(self):
        return f"State(turn={self.turn}, grid={self.grid})"


    def get_moves(self) -> list[State]:

        if self.branches is None:
            self.branches = []

        for i in range(3):
            for j in range(3):
                if self.grid[i][j] == " ":
                    new_grid = [row[:] for row in self.grid]
                    new_grid[i][j] = self.turn
                    self.branches.append(State("X" if self.turn == "O" else "O", new_grid))
        
        return self.branches
    

    def get_evaluation(self) -> float:

        # Check if there is a winner
        # If not, just return whoever's turn it is
        # Range: 0, 1, 2, 3, 4
        # 0: "O" wins
        # 1: "O" goes next
        # 2: Tie
        # 3: "X" goes next
        # 4: "X" wins

        # -------- Check for winner -------- #
        for i in range(3):
            if self.grid[i][0] == self.grid[i][1] == self.grid[i][2] != " ":
                if self.grid[i][0] == "X":
                    return 4.0
                elif self.grid[i][0] == "O":
                    return 0.0

            if self.grid[0][i] == self.grid[1][i] == self.grid[2][i] != " ":
                if self.grid[0][i] == "X":
                    return 4.0
                elif self.grid[0][i] == "O":
                    return 0.0

        if self.grid[0][0] == self.grid[1][1] == self.grid[2][2] != " ":
            if self.grid[0][0] == "X":
                return 4.0
            elif self.grid[0][0] == "O":
                return 0.0

        if self.grid[0][2] == self.grid[1][1] == self.grid[2][0] != " ":
            if self.grid[0][2] == "X":
                return 4.0
            elif self.grid[0][2] == "O":
                return 0.0

        # -------- Check for tie -------- #

        if not any(" " in row for row in self.grid):
            return 2.0

        # -------- Fallback to turn -------- #

        if self.turn == "X":
            return 3.0
        elif self.turn == "O":
            return 1.0
