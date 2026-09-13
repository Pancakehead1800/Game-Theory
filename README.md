
# My Game Theory Projects


Implementing algorithms for game-theory situations is fun. This repository will be my collection for them. Humble beginnings!

<hr style="border: none; border-top: 10px double #333; color: #333; overflow: visible; text-align: center; height: 5px;">


## The Minimax Algorithm

This **Minimax** project will apply the *minimax* algorithm along with common optimizations such as *alpha-beta pruning* for some arbitrary *game*. 

A *game* must include a *State* object, a *Branch* function that acts on a state, and an *Evaluation* function to evaluate a state. 

To run the *minimax* algorithm, simply create an *initial state* and *reference the game file*. An example of a proper game file is given in the `games/` folder. Use the `template.py` file to make a game state that is compatible with the minimax class


## Monte Carlo Simulations

To study anything from a non-liberal perspective, **Monte Carlo** simulations can probably be used. The process, to what I understand, is to simply run many many simulations, where in each simulation, some *non-deterministic* process occurs. The class I implemented allows the user to input some general `trial_function` to represent a singular simulation, then the class runs the simulation as many times as specified and includes some useful plotting methods.


## Payoff Matrices

In simple games with few actions and 2 players, a **Payoff Matrix** is a useful way to determine *Dominant Strategies* and *Nash Equilibria* for each player. That is exactly what the class I implemented can do. However, the current implementation only supports 2x2 matrices like those seen in AP Micro of the Prisoner's Dilemma.
