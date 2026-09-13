
import numpy as np

"""
When simulating the payoff matrix for a cell (i, j),
we need to determine how each player will choose which
strategy/action they will move to.
"""

# Ensure every decision rule can produce a probability
# distribution over a given player's possible actions
class DecisionRule:
    def distribution(self, game, state, player):
        raise NotImplementedError


# Rule: Choose the first action with utility equal to the maximum utility
class GreedyBestRule(DecisionRule):
    def distribution(self, game, state, player):
        # Get the player's possible utilities
        utilities = game.utilities_for_player(state, player)

        # Find the maximum possible utility
        best_utility = utilities.max()

        # Find the first occurance of the value
        best_action = utilities == best_utility
        probabilities = best_action.astype(float)

        return probabilities


# Rule: Choose uniformly over all actions with utility equal to the maximum utility
class UniformBestRule(DecisionRule):
    def distribution(self, game, state, player):
        # Get the player's possible utilities
        utilities = game.utilities_for_player(state, player)

        # Find the maximum possible utility
        best_utility = utilities.max()

        # Find the first occurance of the value (the first/only element of the tuple)
        best_actions = utilities == best_utility

        # Determine probabilities
        probabilities = best_actions.astype(float) / float(best_actions.sum())

        return probabilities


# Rule: Choose randomly over all actions with greater utility
class RandomBeneficialRule(DecisionRule):
    def distribution(self, game, state, player):
        # Get the player's possible utilities
        utilities = game.utilities_for_player(state, player)

        # Find which actions provide higher utility


# Rule:
