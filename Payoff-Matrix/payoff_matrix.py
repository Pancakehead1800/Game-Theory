
from dataclasses import dataclass
from pprint import pprint
from collections import defaultdict
import numpy as np
from decision_rules import (
    GreedyBestRule,
    UniformBestRule,
    RandomBeneficialRule,
)

"""
Payoff Matrix Arguments
1. matrix: An NxNx2 Numpy array representing the payoff matrix
2. player: A tuple (p1:float, p2:float) representing the probability that player 1 or 2 responds first
3. rule:   Which decision rule players will use (see list above)
"""

"""
Total list of strategies (not all implemented yet):
1. Best (maximize utility difference OR uniform choice)
2. Minimax (look ahead a few steps)
3. Ranking (give the moves probability proportionate to ranking)
4. Naive-Random (uniformly choose between actions of higher utility)
5. Pure-Random (Uniformly choose any move)
"""

@dataclass
class Edge:
    target: tuple[int, int]
    probability: float
    player: int
    pre_utility: int
    post_utility: int



class PayoffMatrix:
    def __init__(
        self,
        matrix,
        players=None,
        rules=None
    ):

        # -------- CREATE MATRIX -------- #
        self.matrix = matrix
        if self.matrix is not None:
            # Hope the values are floats
            try:
                self.matrix = np.array(matrix, dtype=float)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Data contains non-numeric entries: {e}")

            # Verify the array has 3 dimensions
            if self.matrix.ndim != 3:
                raise ValueError(f"Expected 3D array, but got {self.matrix.ndim}D array")

            # Verify the final dimension is 2 (for 2x2 players)
            if self.matrix.shape[2] != 2:
                raise ValueError(f"Expected the last dimension to be 2, but got {self.matrix.shape[2]} (Shape: {self.matrix.shape})")
        else:
            self.matrix = self.get_payoff_matrix()

        # -------- CREATE PLAYER PROBABILITIES -------- #
        # self.matrix.shape = (m, n, 2)
        self.m = self.matrix.shape[0]
        self.n = self.matrix.shape[1]

        # -------- CREATE PLAYER PROBABILITIES -------- #
        self.players = players
        if self.players is None:
            self.players = (0.5, 0.5)


        # -------- CREATE PLAYER RULES -------- #
        self.rules = rules
        if self.rules is None:
            self.rules = (GreedyBestRule(), GreedyBestRule())



    # Returns given player's utility for given state
    def utility(self, state, player):
        row, col = state
        return self.matrix[row][col][player]



    # Returns array of alternate utilities that the given player can reach if the other player stays fixed
    def utilities_for_player(self, state: tuple[int, int], player: int):
        row, col = state

        # The index of the np.array is the action number:
        # utilities[Action] = Utility
        if player == 0:
            return self.matrix[:, col, 0]

        elif player == 1:
            return self.matrix[row, :, 1]

        else:
            raise ValueError(f"Player must be 0 or 1 (got {player})")



    # Returns array of probabilities
    def get_player_action_probabilities(self, state, player):
        probabilities = self.rules[player].distribution(self, state, player)
        return probabilities



    # # Determine action given probabilities
    # def choose_user_action(self, probabilities) -> int:
    #     action = np.random.choice(
    #         len(probabilities),
    #         p=probabilities
    #     )
    #     return action



    # Return a weighted, directed graph using dfs
    def simulate_state(self, state) -> dict[tuple: Edge]:
        graph = defaultdict(list)
        seen = set()

        def dfs(state):
            if state in seen:
                return

            seen.add(state)

            # Add the next nodes and their probabilities to the graph
            player_0_probabilities = self.get_player_action_probabilities(state, 0) * self.players[0]
            player_1_probabilities = self.get_player_action_probabilities(state, 1) * self.players[1]

            # Player 0 probabilities
            for action, probability in enumerate(player_0_probabilities):
                # tolerance is 5e-3 = 0.005 = 0.5%
                if probability > 5e-3:
                    target = (action, state[1])
                    graph[state].append(Edge(
                        target=target,
                        probability=probability,
                        player=0,
                        pre_utility=self.utility(state, 0),
                        post_utility=self.utility(target, 0)
                    ))

            # Player 1 probabilities
            for action, probability in enumerate(player_1_probabilities):
                if probability > 5e-3:
                    target = (state[0], action)
                    graph[state].append(Edge(
                        target=target,
                        probability=probability,
                        player=1,
                        pre_utility=self.utility(state, 1),
                        post_utility=self.utility(target, 1)
                    ))

            # Perform dfs on next nodes
            for action, _ in enumerate(player_0_probabilities):
                next_state = (action, state[1])
                dfs(next_state)

            for action, _ in enumerate(player_1_probabilities):
                next_state = (state[0], action)
                dfs(next_state)

        dfs(state)
        return graph



    # Prompts the user for the payoff matrix
    def get_payoff_matrix(self):
        pass



if __name__ == "__main__":
    import json

    # Open the file and load its content
    with open('text.json', 'r') as file:
        matrix = json.load(file)
        pprint(matrix)
        print()

        pm = PayoffMatrix(
            matrix=matrix,
            players=(1,0),
            rules=(UniformBestRule(), UniformBestRule())
        )

        test = pm.simulate_state((0,0))
        pprint(test)
