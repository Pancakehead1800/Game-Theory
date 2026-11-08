
import numpy as np

"""
When simulating the payoff matrix for a cell (i, j),
we need to determine how each player will choose which
strategy/action they will move to.
"""

# ensure every decision rule can produce a probability distribution over a given player's possible actions
class DecisionRule:
    def distribution(self, game, state, player):
        raise NotImplementedError


# rule: choose the first action with utility equal to the maximum utility
class GreedyBestRule(DecisionRule):
    def distribution(self, game, state, player):
        # Get the player's possible utilities
        utilities = game.get_utilities_for_player(state, player)

        # Use the first occurrence of the maximum utility
        probabilities = np.zeros_like(utilities)
        probabilities[np.argmax(utilities)] = 1.0

        return probabilities


# rule: choose uniformly over all actions with utility equal to the maximum utility
class UniformBestRule(DecisionRule):
    def distribution(self, game, state, player):
        # get the player's possible utilities
        utilities = game.get_utilities_for_player(state, player)

        # find the maximum possible utility
        best_utility = utilities.max()

        # find the first occurrence of the value (the first/only element of the tuple)
        best_actions = utilities == best_utility
        n_actions = best_actions.sum()

        # determine probabilities
        probabilities = best_actions.astype(float) / float(n_actions)

        return probabilities


# rule: choose randomly over all actions with greater utility
class RandomBeneficialRule(DecisionRule):
    def distribution(self, game, state, player):
        # get the player's possible utilities
        utilities = game.get_utilities_for_player(state, player)
        current_utility = game.get_utility(state, player)

        # find which actions provide higher utility
        better_actions = utilities > current_utility
        choices = better_actions.sum()

        # With no strictly better action, keep the current action.
        if choices == 0:
            probabilities = np.zeros_like(utilities)
            probabilities[state[player]] = 1.0
            return probabilities

        # determine probabilities
        probabilities = better_actions.astype(float) / float(choices)

        return probabilities

# rule: completely random
class PureRandomRule(DecisionRule):
    def distribution(self, game, state, player):
        size = game.m if player == 0 else game.n
        probabilities = np.ones(size) / size
        return probabilities
