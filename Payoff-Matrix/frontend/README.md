# State / Space

A plain HTML/CSS/JavaScript frontend for the Python payoff-matrix project.
No frontend dependencies or build step. All game rules run in Python.

## Run

From the repository root, use a Python environment with NumPy installed:

```sh
python3 Payoff-Matrix/api.py
```

Open http://127.0.0.1:8000. Add `--port 8001` to use a different port.
Restart the server after Python edits; reload the page after frontend edits.

## Where to work

| File | Responsibility |
| --- | --- |
| `../decision_rules.py` | Player decision rules. |
| `../payoff_matrix.py` | Utilities and the graph of possible responses. |
| `../api.py` | Rule-name lookup, graph serialization, request validation, local server. |
| `app.js` | Matrix editor, API request, playback controls, heatmap and metrics. |
| `dynamics.mjs` | Validate the returned graph and propagate its probabilities into frames. |
| `charts.js` | Draw flow arrows and the expected-payoff chart. |
| `index.html` | Page structure and control labels. |
| `styles.css` | App layout, matrix cells, animation and responsive styles. |
| `algory.css` | Shared ALGORY colors and base component styles. |

The flow is:

1. The editor sends the matrix, starting cell, turn probabilities, and rule names.
2. `build_transition_graph()` constructs your game, calls `simulate_state()`, and
   serializes the graph.
3. JavaScript validates the graph and calculates each frame's probability mass.
4. Playback displays those frames. It does not choose moves or implement rules.

To expose another decision rule, register its class in `api.py`'s `RULES` mapping
and add its key to both decision-rule selects in `index.html`. Make sure the rule
returns a valid probability distribution even when there is no beneficial move.

## API contract

`POST /api/simulate` accepts JSON:

```json
{
  "matrix": [[[3, 2], [0, 0]], [[0, 0], [2, 3]]],
  "start": [0, 1],
  "players": [0.5, 0.5],
  "rules": ["greedy_best", "uniform_best"]
}
```

The response has one node per state, each containing an `edges` list:

```json
{
  "nodes": [
    {"state": [0, 1], "edges": [
      {"target": [1, 1], "probability": 0.5, "player": 0},
      {"target": [0, 0], "probability": 0.5, "player": 1}
    ]},
    {"state": [1, 1], "edges": [
      {"target": [1, 1], "probability": 0.5, "player": 0},
      {"target": [1, 1], "probability": 0.5, "player": 1}
    ]},
    {"state": [0, 0], "edges": [
      {"target": [0, 0], "probability": 0.5, "player": 0},
      {"target": [0, 0], "probability": 0.5, "player": 1}
    ]}
  ]
}
```

All API indices are zero-based; displayed row and column labels start at 1.
Player 0 changes rows; player 1 changes columns. Edge probabilities include the
chance of selecting that player. Every node's outgoing probabilities must total
1, and every destination must have a node. Absorbing states still need self-loops.

**Backend requirement:** a nonzero `simulate_state()` tolerance filters out
probabilities at or below that threshold. This can produce an incomplete distribution for
unequal turn probabilities or many tied actions. The frontend reports that error
instead of renormalizing it. Use a zero cutoff for a complete graph when extending
the backend. The cleanup preserves the existing Python game behavior.

## Animation

At step zero all probability is at the selected cell. Each update calculates:

```text
next[target] += current[source] * edge.probability
```

The animation shows a distribution, not a sampled path or a Nash-equilibrium
solution. The chart shows expected payoffs across that distribution.

- Lower-left payoff: P1. Upper-right payoff: P2.
- Cell brightness uses a fixed square-root probability scale from 0 to 100%.
- Arrows show moves from the previous frame. Self-loops have no arrow.
- For readability, only the 60 largest moving flows above 0.01% are drawn.
  This display limit does not remove probability from the calculation.
- Editing the game invalidates its cached graph and frames. Reset returns to the
  initial frame; resetting during a request cancels the request.
- Resize preserves overlapping cells and initializes new cells to `[0, 0]`.
- Limits: 12 × 12 cells, 200 steps, payoffs between ±1,000,000.
- Reduced-motion preferences disable cell transitions and moving arrow dashes.
