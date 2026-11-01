"""Local frontend server and payoff-matrix API. Run: python3 Payoff-Matrix/api.py.

The frontend does distribution propagation and animation; Python supplies edges.
Game calculations use NumPy; HTTP hosting uses the Python standard library.
"""

import argparse
import json
import math
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from payoff_matrix import PayoffMatrix
from decision_rules import (
    GreedyBestRule,
    UniformBestRule,
    RandomBeneficialRule,
)

FRONTEND = Path(__file__).parent / "frontend"

RULES = {
    "greedy_best": GreedyBestRule,
    "uniform_best": UniformBestRule,
    "random_beneficial": RandomBeneficialRule
}


def build_transition_graph(matrix, start, players, rules):
    """Run the game and return one node per state, with its outgoing edges.

    State and player indices are zero-based. Edge probabilities already include
    the chance of selecting that player. See frontend/README.md for the contract.
    """

    # Point the strings in "rules" to the actual objects
    rules = tuple(RULES[rule]() for rule in rules)

    pm = PayoffMatrix(matrix, players=players, rules=rules)
    transition_graph = pm.simulate_state(tuple(start))

    # Convert graph into JSON-serializable object
    res = {"nodes": []}
    for state, edges in transition_graph.items():
        node = {
            "state": list(state),
            "edges": []
        }

        for edge in edges:
            node["edges"].append({
                "target": list(edge.target),
                "probability": float(edge.probability),
                "player": edge.player
            })

        res["nodes"].append(node)

    return res


def validate_request(data):
    """Transport validation only; no game logic is implemented here."""
    def finite_number(value):
        return type(value) in (float, int) and math.isfinite(value)

    if not isinstance(data, dict):
        raise ValueError("Request must be a JSON object.")
    matrix = data.get("matrix")
    if not isinstance(matrix, list) or not 1 <= len(matrix) <= 12:
        raise ValueError("Matrix must have 1–12 rows.")
    if not isinstance(matrix[0], list) or not 1 <= len(matrix[0]) <= 12:
        raise ValueError("Matrix must have 1–12 columns.")
    n = len(matrix[0])
    for row in matrix:
        if not isinstance(row, list) or len(row) != n:
            raise ValueError("Matrix must be rectangular.")
        for cell in row:
            if (not isinstance(cell, list) or len(cell) != 2 or
                    any(not finite_number(v) or abs(v) > 1_000_000 for v in cell)):
                raise ValueError("Each cell needs two finite payoffs between −1,000,000 and 1,000,000.")
    start = data.get("start")
    if (not isinstance(start, list) or len(start) != 2 or
            any(type(v) is not int for v in start) or
            not 0 <= start[0] < len(matrix) or not 0 <= start[1] < n):
        raise ValueError("Start must be a valid zero-based [row, column].")
    players = data.get("players")
    if (not isinstance(players, list) or len(players) != 2 or
            any(not finite_number(p) or not 0 <= p <= 1 for p in players) or
            abs(sum(players) - 1) > 1e-8):
        raise ValueError("Player probabilities must sum to 1.")
    rules = data.get("rules")
    if (not isinstance(rules, list) or len(rules) != 2 or
            any(not isinstance(rule, str) or rule not in RULES for rule in rules)):
        raise ValueError(f"Choose one of these rules for each player: {', '.join(RULES)}.")
    return matrix, start, players, rules


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND), **kwargs)

    def send_json(self, status, payload):
        body = json.dumps(payload, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/api/simulate":
            self.send_json(404, {"error": "Unknown endpoint."})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 100_000:
                raise ValueError("Request body must be 1–100,000 bytes.")
            payload = json.loads(self.rfile.read(size))
            args = validate_request(payload)
        except (ValueError, OverflowError) as error:
            self.send_json(400, {"error": str(error)})
            return
        try:
            result = build_transition_graph(*args)
            self.send_json(200, result)
        except Exception as error:
            self.log_error("Simulation failed: %s", error)
            self.send_json(500, {"error": "Simulation failed. See the Python server terminal."})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"State / Space: http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
