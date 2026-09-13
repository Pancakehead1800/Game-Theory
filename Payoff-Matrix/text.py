import numpy as np
from pathlib import Path
import json

rng = np.random.default_rng(42)

m, n = 20, 25

# Start with varied integer payoffs.
payoffs = rng.integers(-9, 16, size=(m, n, 2), dtype=np.int64)

# Add several structured "attractor" cells that are mutual best-response candidates.
# We shape rows/columns locally rather than making the entire game trivial.
targets = [
    (2, 4, 18, 17),
    (7, 13, 16, 19),
    (15, 21, 20, 16),
]

for i, j, p1, p2 in targets:
    # Make row i unusually attractive for Player 1 when Player 2 chooses column j.
    payoffs[:, j, 0] = np.minimum(payoffs[:, j, 0], p1 - 2)
    payoffs[i, j, 0] = p1

    # Make column j unusually attractive for Player 2 when Player 1 chooses row i.
    payoffs[i, :, 1] = np.minimum(payoffs[i, :, 1], p2 - 2)
    payoffs[i, j, 1] = p2

# Add one strictly dominated row for Player 1:
# row 19 is made worse than row 0 in every column.
payoffs[19, :, 0] = payoffs[0, :, 0] - rng.integers(1, 6, size=n)

# Add one strictly dominated column for Player 2:
# column 24 is made worse than column 1 in every row.
payoffs[:, 24, 1] = payoffs[:, 1, 1] - rng.integers(1, 6, size=m)

# Save useful formats.
outdir = Path("/mnt/data")
npy_path = outdir / "payoff_matrix_20x25x2.npy"
json_path = outdir / "payoff_matrix_20x25x2.json"
py_path = outdir / "payoff_matrix_20x25x2.py"

np.save(npy_path, payoffs)

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(payoffs.tolist(), f)

with open(py_path, "w", encoding="utf-8") as f:
    f.write(
        "import numpy as np\n\n"
        "# Shape: (20, 25, 2)\n"
        "# matrix[i, j] = [player1_payoff, player2_payoff]\n"
        "PAYOFF_MATRIX = np.array(\n"
        + repr(payoffs.tolist())
        + ", dtype=int)\n"
    )

print("Shape:", payoffs.shape)
print("Example cell (2, 4):", payoffs[2, 4].tolist())
print("Files created:")
print(npy_path)
print(json_path)
print(py_path)

