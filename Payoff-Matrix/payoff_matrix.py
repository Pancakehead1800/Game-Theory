
from dataclasses import dataclass
from pprint import pprint
from copy import deepcopy
from collections import defaultdict
import numpy as np
from decision_rules import (
    GreedyBestRule,
    UniformBestRule,
    RandomBeneficialRule,
    PureRandomRule
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


RULES = {
    "greedy_best": GreedyBestRule,
    "uniform_best": UniformBestRule,
    "random_beneficial": RandomBeneficialRule,
    "pure_random": PureRandomRule
}


class PayoffMatrix:
    def __init__(
        self,
        matrix=None, # m x n x 2 matrix representing the matrix of player utilities
        players=None, # tuple[float, float] representing probability of it being someone's turn
        rules=None, # tuple[Rule, Rule] representing the default decision rules for each player
        damping=0, # float representing the damping value for each player's transitioning
    ):
        self.update_matrix(matrix)
        self.update_players(players)
        self.update_rules(rules)
        self.update_damping(damping)


    # ======== DATA RETRIEVAL METHODS ======== #

    # returns given player's utility for given state
    def get_utility(self, state, player):
        row, col = state
        return self.matrix[row][col][player]

    # returns array of alternate utilities that the given player can reach if the other player stays fixed
    def get_utilities_for_player(self, state: tuple[int, int], player: int):
        row, col = state

        # The index of the np.array is the action number:
        # utilities[Action] = Utility
        if player == 0:
            return self.matrix[:, col, 0]

        elif player == 1:
            return self.matrix[row, :, 1]

        else:
            raise ValueError(f"Player must be 0 or 1 (got {player})")

    # returns array of probabilities
    def get_player_action_probabilities(self, state, player):
        # add damping before computing probabilities, then remove it after
        original = self.matrix[state[0], state[1], player]
        self.matrix[state[0], state[1], player] = original + self.damping
        probabilities = self.rules[player].distribution(self, state, player)
        self.matrix[state[0], state[1], player] = original
        return probabilities



    # ======== DATA UPDATING METHODS ======== #

    # update the matrix
    def update_matrix(self, new_matrix):
        if new_matrix is None:
            raise ValueError("No matrix was given!")

        # setup matrix as a numpy array
        try:
            self.matrix = np.array(new_matrix, dtype=float)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Data contains non-numeric entries: {e}")

        # Verify the array has 3 dimensions
        if self.matrix.ndim != 3:
            raise ValueError(f"Expected 3D array, but got {self.matrix.ndim}D array")

        # Verify the final dimension is 2 (for 2x2 players)
        if self.matrix.shape[2] != 2:
            raise ValueError(f"Expected the last dimension to be 2, but got {self.matrix.shape[2]} (Shape: {self.matrix.shape})")

        # matrix shape
        self.m = self.matrix.shape[0]
        self.n = self.matrix.shape[1]

    # update player turns probabilities
    def update_players(self, new_players):
        # set player turn probabilities
        self.players = new_players
        if self.players is None:
            self.players = (0.5, 0.5)

    # update the player rules
    def update_rules(self, new_rules):
        # set player rules
        self.rules = new_rules
        if self.rules is None:
            self.rules = (GreedyBestRule(), GreedyBestRule())

    # update damping value
    def update_damping(self, damping):
        self.damping = damping


    # ======== ANALYSIS METHODS ======== #

    # return a weighted, directed graph using dfs
    def simulate_state(self, state, tolerance=1e-9) -> dict[tuple[int, int], list[Edge]]:
        graph = defaultdict(list)
        seen = set()

        def dfs(source):
            if source in seen:
                return

            seen.add(source)

            for player in (0, 1):
                # Add the next nodes and their probabilities to the graph
                probabilities = self.get_player_action_probabilities(source, player) * self.players[player]

                for action, probability in enumerate(probabilities):
                    if probability > tolerance:
                        target = (action, source[1]) if player == 0 else (source[0], action)
                        graph[source].append(Edge(
                            target=target,
                            probability=probability,
                            player=player,
                            pre_utility=self.get_utility(source, player),
                            post_utility=self.get_utility(target, player)
                        ))

                        next_state = (action, source[1]) if player == 0 else (source[0], action)
                        dfs(next_state)

        dfs(state)
        return graph


    # store the frames of the simulation (i.e. split the graph into levels and determine some other useful data)
    def simulate_frames(self, state, steps):
        # initial graph
        graph = self.simulate_state(state)

        # lists for storing step data
        sources, targets, probabilities, players = [], [], [], []

        for source, edges in graph.items():
            for edge in edges:
                # encoding states by enumerating matrix entires 0 ... m*n-1, right to left then top to bottom
                sources.append(source[0] * self.n + source[1])
                targets.append(edge.target[0] * self.n + edge.target[1])
                probabilities.append(edge.probability)
                players.append(edge.player)

        # convert to numpy
        sources, targets = np.array(sources), np.array(targets)
        probabilities = np.array(probabilities)

        # using the encoding, things are maybe easier?
        mass = np.zeros(self.m * self.n)
        mass[state[0] * self.n + state[1]] = 1

        # keep track of flows
        frames, flows = [], []
        for step in range(steps+1):
            maximum = float(mass.max())
            frames.append({
                "mass": mass.tolist(),
                "utilities": (mass @ self.matrix.reshape(-1, 2)).tolist(),
                "most_likely": int(mass.argmax()),
                "maximum": maximum,
                "ties" : int(np.count_nonzero(np.abs(mass - maximum) < 1e-10)),
                "flows" : flows,
            })

            if step == steps:
                break

            # more flow stuff
            amounts = mass[sources] * probabilities
            visible = np.flatnonzero((sources != targets) & (amounts > 1e-5))
            visible = sorted(visible, key=lambda i: (-amounts[i], i))[:60]
            flows = [
                {"source": int(sources[i]), 
                 "target": int(targets[i]),
                 "amount": float(amounts[i]),
                 "player": players[i]
                } for i in visible
            ]

            mass = np.bincount(targets, weights=amounts, minlength=mass.size)

        return graph, frames


# create random data
def create_random_data(m, n, lower_bound=-10, upper_bound=10, seed=None):

    # create generator
    rng = np.random.default_rng(seed=seed)

    # generate matrix
    matrix = rng.integers(low=lower_bound, high=upper_bound, size=(m, n, 2), dtype=int)

    # generate player turn probabilities
    p1 = np.round(rng.random(), 6)
    players = (p1, 1.0 - p1)

    # generate rules
    rules = tuple(rule for rule in rng.choice(RULES.keys(), size=2))

    # generate damping value
    damping = rng.exponential(scale=1.0)
    damping = np.clip(damping, 0, 20)

    return matrix, players, rules, damping


# cool example matrices
EXAMPLES = {
    "rock_paper_scissors" :
        [
            [ [0, 0], [-1, 1], [1,-1] ],
            [ [1,-1], [ 0, 0], [-1,1] ],
            [ [-1,1], [ 1,-1], [0, 0] ]
        ],
    "prisoners_dilemma_2x2" :
        [
            [ [1, 1], [5, 0] ],
            [ [0, 5], [3, 3] ],
        ],
    "coordination" :
        [
            [ [3, 2], [0, 0] ],
            [ [0, 0], [2, 3] ]
        ]
}


def get_example(example: str):
    """Return an independent editable copy of a named example."""
    if example not in EXAMPLES:
        raise ValueError(f"Unknown example: {example}. Choose from {', '.join(EXAMPLES)}.")
    return deepcopy(EXAMPLES[example])



if __name__ == "__main__":
    import json

    # Open the file and load its content
    with open('text.json', 'r') as file:
        matrix = json.load(file)

        pm = PayoffMatrix(
            matrix=matrix,
            players=(0.5,0.5),
            rules=(GreedyBestRule(), UniformBestRule()),
            damping=1
        )

        test = pm.simulate_state((0,0))
        pprint(test)
