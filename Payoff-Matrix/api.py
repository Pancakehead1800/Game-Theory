

import argparse
import math
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from payoff_matrix import PayoffMatrix, create_random_data, RULES, EXAMPLES, get_example
from decision_rules import GreedyBestRule, UniformBestRule, RandomBeneficialRule

app = FastAPI(title="Payoff Matrix", version="1.0.0")

RULE_LABELS = {
    "greedy_best": "First best action",
    "uniform_best": "Random among best",
    "random_beneficial": "Random among improvements",
    "pure_random": "Complete random moves"
}


# ======== Endpoint functions ======== #

# expose predefined examples and explain usable decision rules
@app.get("/api/catalog")
def catalog():
    return {
        "examples": [{
            "id": key, 
            "label": key.replace("_", " ").capitalize(),
            "matrix": get_example(key)
            } for key in EXAMPLES 
        ],
        "rules": [{
            "id": key, 
            "label": RULE_LABELS.get(key, key.replace("_", " "))
            } for key in RULES 
        ],
    }


# simulate some given graph
@app.post("/api/simulate")
def simulate(data: dict):
    # get required values from data
    matrix, start, players, rules, damping = prepare_matrix_data(data)
    steps = data.get("steps", 40)
    rules = tuple(RULES[rule]() for rule in rules)

    # create and simulate matrix
    pm = PayoffMatrix(matrix, players=players, rules=rules, damping=damping)
    graph, frames = pm.simulate_frames(tuple(start), steps)

    # create formatted result
    return {
        "nodes": [{
            "state": state,
            "edges": [{
                "target": edge.target,
                "probability": edge.probability,
                "player": edge.player,
                "pre_utility": edge.pre_utility,
                "post_utility": edge.post_utility
            } for edge in edges ],
        } for state, edges in graph.items() ],
        "frames": frames
    }


# get a random configuration
@app.post("/api/randomize")
def get_random_data(data: dict):
    # get random data
    matrix, players, rules, damping = prepare_random_data(data)

    return {"matrix": matrix.tolist(), 
            "start": [0, 0],
            "players": [float(p) for p in players],
            "rules": rules, 
            "damping": float(damping)}



# ======== Functions for preparing data ======== #

# prepare the random data inputs
def prepare_random_data(data):
    if not isinstance(data, dict):
        raise ValueError("Request must be a JSON object.")

    # helper function for checking numbers
    def _finite_number(value):
        return type(value) in (float, int) and abs(value) <= 1_000_000 and math.isfinite(value)

    # check dimensions
    m, n = data.get("m", 3), data.get("n", 3)
    if not isinstance(m, int) or not _finite_number(m) or m < 2:
        raise ValueError("Number of rows must be finite and at least 2")
    if not isinstance(n, int) or not _finite_number(n) or n < 2:
            raise ValueError("Number of columns must be finite and at least 2")

    # check bounds
    lower_bound, upper_bound = data.get("lower_bound", -10), data.get("upper_bound", 10)
    if not isinstance(lower_bound, int) or not _finite_number(lower_bound):
        raise ValueError("Lower bound must be a finite integer")
    if not isinstance(upper_bound, int) or not _finite_number(upper_bound):
        raise ValueError("Upper bound must be a finite integer")
    if upper_bound < lower_bound:
        raise ValueError("Upper bound must be greater than lower bound!")

    # check seed
    seed = data.get("seed", 42)
    if not isinstance(seed, int) or not _finite_number(seed):
        raise ValueError("Randomization seed is not a finite integer!")

    random_matrix, random_players, random_rules, random_damping = create_random_data(m, n, lower_bound=lower_bound, upper_bound=upper_bound, seed=seed)
    return random_matrix, random_players, random_rules, random_damping
    
    
# prepare the matrix data input
def prepare_matrix_data(data):
    if not isinstance(data, dict):
        raise ValueError("Request must be a JSON object.")

    # helper function for checking numbers
    def _finite_number(value):
        return type(value) in (float, int) and abs(value) <= 1_000_000 and math.isfinite(value)

    # get matrix data
    matrix = data.get("matrix")
    # check rows
    if not isinstance(matrix, list) or not 1 <= len(matrix) <= 50:
        raise ValueError("Matrix must have 1-50 rows")
    # check columns
    if not isinstance(matrix[0], list) or not 1 <= len(matrix[0]) <= 50:
        raise ValueError("Matrix must have 1-50 columns.")
    # check values in rows
    n = len(matrix[0])
    for row in matrix:
        if not isinstance(row, list) or len(row) != n:
            raise ValueError("Matrix must be rectangular.")
        for cell in row:
            if (not isinstance(cell, list) or len(cell) != 2 or any(not _finite_number(v) or abs(v) > 1_000_000 for v in cell)):
                raise ValueError("Each cell needs two finite payoffs between -1,000,000 and 1,000,000.")

    # get starting point
    start = data.get("start")
    if (not isinstance(start, list) or len(start) != 2 or any(type(v) is not int for v in start) or not 0 <= start[0] < len(matrix) or not 0 <= start[1] < n):
        raise ValueError("Start must be a valid zero-based [row, column].")

    # get player data
    players = data.get("players")
    if (not isinstance(players, list) or len(players) != 2 or any(not _finite_number(p) or not 0 <= p <= 1 for p in players) or abs(sum(players) - 1) > 1e-8):
        raise ValueError("Player probabilities must sum to 1.")

    # get rule data
    rules = data.get("rules")
    if not isinstance(rules, list) or len(rules) != 2:
        raise ValueError(f"Choose one of these rules for each player: {', '.join(RULES)}.")

    # get damping data
    damping = data.get("damping", 0)
    if not _finite_number(damping) or not 0 <= damping <= 1_000_000:
        raise ValueError("Damping must be a finite number between 0 and 1,000,000.")

    return matrix, start, players, rules, damping


# mount the frontend
app.mount("/", StaticFiles(directory=Path(__file__).parent / "frontend", html=True), name="frontend")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run(app, host="127.0.0.1", port=args.port)
