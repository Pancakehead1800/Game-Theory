# Payoff matrix playground

A small, build-free visual demo: plain HTML, CSS, JavaScript, and SVG.
The Python backend owns all simulation calculations. The frontend edits the
matrix and plays back returned frames; it never calculates moves or payoffs.

## Run

From the repository root:

```sh
.venv/bin/python Payoff-Matrix/api.py
```

Open http://127.0.0.1:8000. The same server serves the page and API;
opening `index.html` directly will not work. Restart after Python changes and
reload after frontend changes. Interactive API documentation is at `/docs`.

## Files

- `index.html`: matrix editor, settings, playback, and payoff chart.
- `styles.css`: layout, colors, and animated arrows; no external fonts.
- `app.js`: API requests, editing, playback, and displaying returned metrics.
- `charts.js`: draw arrows and payoff lines using SVG.
- `damping.js`: synchronize the exact value, slider, and adjustable bounds.

`algory.css` is an older stylesheet and is no longer loaded.

## What the frontend expects

- `GET /api/catalog`: `{examples: [{id, label, matrix}], rules: [{id, label}]}`.
- `POST /api/simulate`: accepts `matrix`, `start`, `players`, `rules`, `damping`,
  and `steps`. Returns `frames` with `steps + 1` entries, including step zero.
  Each frame contains `mass`, `utilities`, `most_likely`, `maximum`, `ties`,
  and `flows`. Extra response fields such as `nodes` are unused by the viewer.
- `POST /api/randomize`: accepts `m`, `n`, `lower_bound`, `upper_bound`, and
  `seed`. Returns `matrix`, `start`, `players`, `rules`, and `damping`.
  **Rules must be catalog IDs (strings), not Python classes or instances.**

State indices are zero-based in requests and responses, displayed from 1.
Mass entries and flow source/target indices use row-major order. P1 changes
rows; P2 changes columns. Each flow includes `source`, `target`, `amount`,
and `player`. The frontend only draws the flows supplied by Python.

Random game sends explicit bounds −10 to 10 (upper exclusive) and a fresh
integer seed. The current random API requires at least 2×2 dimensions.
Examples replace just the matrix and start; random games replace settings too.
Resizing keeps overlapping cells. Editing a game discards its previous frames
and cancels pending requests. Reset returns to step zero.

The chart shows expected original payoffs, without deducting switching costs.
Damping slider bounds are local editor preferences. They are under “Slider
range”; only the exact damping value is sent to Python.

## Errors and current verification limit

API failures appear beside the playback controls. A plain HTTP 500 response
points you to the Python traceback rather than showing a misleading JSON error.
The catalog can be retried without reloading the page.

At this cleanup, the live catalog and editor work, but the current Python API
blocks simulation and random-game requests. The issues were reported to the
owner for manual repair; no core or API implementation was changed. Playback
still consumes the existing frame format. End-to-end playback needs rechecking
after those backend repairs.
