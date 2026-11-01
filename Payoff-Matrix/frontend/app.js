import { validateGraph, evolve } from './dynamics.mjs';
import { drawFlows, drawPayoffChart } from './charts.js';

const element = id => document.getElementById(id);
const PRESETS = {
  cycle: [
    [[0, 0], [-1, 1], [1, -1]],
    [[1, -1], [0, 0], [-1, 1]],
    [[-1, 1], [1, -1], [0, 0]],
  ],
  coordination: [[[3, 2], [0, 0]], [[0, 0], [2, 3]]],
  dilemma: [[[2, 2], [-1, 3]], [[3, -1], [0, 0]]],
};

// Editor and playback state. Graphs and frames are discarded after game edits.
let matrix = structuredClone(PRESETS.cycle);
let start = [0, 0];
let graph = null;
let frames = [];
let currentStep = 0;
let playing = false;
let playbackTimer = null;
let pendingRequest = null;
let revision = 0;

function percentage(probability) {
  const decimals = probability > 0 && probability < 0.01 ? 2 : 1;
  return `${(100 * probability).toFixed(decimals)}%`;
}

function stateLabel(index) {
  const columns = matrix[0].length;
  return `(${Math.floor(index / columns) + 1}, ${index % columns + 1})`;
}

function showStatus(message, isError = false) {
  element('status').textContent = message;
  element('status').classList.toggle('error', isError);
}

function pause() {
  playing = false;
  clearTimeout(playbackTimer);
  element('simulate').textContent = '▶ Simulate';
  document.body.classList.add('paused');
}

function setLoading(loading) {
  element('simulate').disabled = loading;
  element('step').disabled = loading;
}

function initialFrame() {
  const mass = Array(matrix.length * matrix[0].length).fill(0);
  mass[start[0] * matrix[0].length + start[1]] = 1;
  return { mass, utilities: matrix[start[0]][start[1]] };
}

function invalidateSimulation(message = 'Ready. Choose a starting cell, then simulate.') {
  // Ignore responses for an older matrix if the user edits during a request.
  revision++;
  pendingRequest?.abort();
  pendingRequest = null;
  pause();
  graph = null;
  frames = [];
  currentStep = 0;
  setLoading(false);
  element('timeline').disabled = true;
  showStatus(message);
  renderFrame();
}

// Matrix editor -------------------------------------------------------------

function axisLabel(text) {
  const label = document.createElement('span');
  label.className = 'axis';
  label.textContent = text;
  return label;
}

function payoffInput(row, column, player) {
  const input = document.createElement('input');
  input.type = 'number';
  input.step = 'any';
  input.min = '-1000000';
  input.max = '1000000';
  input.required = true;
  input.className = `utility p${player + 1}`;
  input.value = matrix[row][column][player];
  input.setAttribute('aria-label',
    `Row ${row + 1}, column ${column + 1}, player ${player + 1} payoff`);

  input.addEventListener('input', () => {
    if (input.checkValidity() && Number.isFinite(input.valueAsNumber)) {
      matrix[row][column][player] = input.valueAsNumber;
    }
    element('example').value = 'custom';
    invalidateSimulation('Payoff edited. Simulate again to update the distribution.');
  });
  return input;
}

function matrixCell(row, column) {
  const cell = document.createElement('div');
  cell.className = 'cell';
  cell.dataset.index = row * matrix[0].length + column;
  cell.innerHTML = `
    <button class="cell-start" type="button"></button>
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
      <line x1="0" y1="0" x2="100" y2="100" />
    </svg>
    <span class="start-tag"></span>
    <span class="probability"></span>
  `;
  const button = cell.querySelector('button');
  button.setAttribute('aria-label', `Start at row ${row + 1}, column ${column + 1}`);
  button.addEventListener('click', () => {
    start = [row, column];
    invalidateSimulation(`Starting at row ${row + 1}, column ${column + 1}. Press Simulate.`);
  });
  cell.append(payoffInput(row, column, 0), payoffInput(row, column, 1));
  return cell;
}

function renderMatrix() {
  const rows = matrix.length;
  const columns = matrix[0].length;
  element('rows').value = rows;
  element('cols').value = columns;
  element('shape').textContent = `${rows} × ${columns} × 2`;

  const grid = element('matrix');
  grid.replaceChildren(document.createElement('span'));
  grid.style.gridTemplateColumns = `28px repeat(${columns}, minmax(112px, 1fr))`;
  element('matrix-stage').style.width = `max(100%, ${36 + columns * 120}px)`;

  for (let column = 0; column < columns; column++) {
    grid.append(axisLabel(`C${column + 1}`));
  }
  for (let row = 0; row < rows; row++) {
    grid.append(axisLabel(`R${row + 1}`));
    for (let column = 0; column < columns; column++) {
      grid.append(matrixCell(row, column));
    }
  }
  renderFrame();
}

function heatColor(probability) {
  const cold = [18, 23, 42];
  const hot = [53, 104, 166];
  // The scale stays fixed across frames, rather than rescaling to the maximum.
  const intensity = Math.sqrt(probability);
  const channels = cold.map((value, channel) => {
    return Math.round(value + (hot[channel] - value) * intensity);
  });
  return `rgb(${channels.join(',')})`;
}

function renderFlows() {
  drawFlows(graph, frames[currentStep - 1], matrix[0].length, element('show-flows').checked);
}

function renderFrame() {
  const frame = frames[currentStep] || initialFrame();
  const startIndex = start[0] * matrix[0].length + start[1];
  for (const cell of document.querySelectorAll('.cell')) {
    const index = Number(cell.dataset.index);
    const probability = frame.mass[index] ?? 0;
    const selected = index === startIndex;
    cell.classList.toggle('selected', selected);
    cell.querySelector('button').setAttribute('aria-pressed', String(selected));
    cell.querySelector('.start-tag').textContent = selected ? 'START' : '';
    const label = cell.querySelector('.probability');
    label.textContent = percentage(probability);
    label.style.color = probability > 0.01 ? 'var(--text-primary)' : '';
    cell.style.backgroundColor = heatColor(probability);
  }

  const maximum = Math.max(...frame.mass);
  const mostLikely = frame.mass.indexOf(maximum);
  const ties = frame.mass.filter(probability => Math.abs(probability - maximum) < 1e-10).length;
  const tieLabel = ties > 1 ? ` · ${ties} states tied` : '';
  element('start-metric').textContent = stateLabel(startIndex);
  element('likely-metric').textContent = stateLabel(mostLikely);
  element('likely-detail').textContent = `${percentage(maximum)} probability${tieLabel}`;
  element('u1').textContent = frame.utilities[0].toFixed(2);
  element('u2').textContent = frame.utilities[1].toFixed(2);

  const lastStep = frames.length ? frames.length - 1 : Number(element('steps').value) || 40;
  element('step-label').textContent = `Step ${String(currentStep).padStart(2, '0')} / ${lastStep}`;
  element('timeline').max = lastStep;
  element('timeline').value = currentStep;
  element('end-label').textContent = `${lastStep} updates`;
  renderFlows();
  drawPayoffChart(frames.length ? frames : [frame], currentStep);
}

// API and playback ----------------------------------------------------------

function validateInputs() {
  const inputs = [...document.querySelectorAll('.utility'), element('steps')];
  for (const input of inputs) {
    if (!input.checkValidity()) {
      input.reportValidity();
      throw new Error('Enter valid payoffs (−1,000,000 to 1,000,000) and 1–200 steps.');
    }
  }
}

async function requestGraph(signal) {
  const playerProbability = Number(element('player-prob').value) / 100;
  const response = await fetch('/api/simulate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    signal,
    body: JSON.stringify({
      matrix,
      start,
      players: [playerProbability, 1 - playerProbability],
      rules: [element('rule1').value, element('rule2').value],
    }),
  });

  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error('The API did not return JSON. Start api.py and open its local URL.');
  }
  if (!response.ok) throw new Error(data.error || `API error ${response.status}`);
  return data;
}

async function prepareSimulation() {
  validateInputs();
  if (frames.length) return true;

  const requestedRevision = revision;
  const controller = new AbortController();
  pendingRequest = controller;
  setLoading(true);
  showStatus('Requesting the response graph from Python…');
  const timeout = setTimeout(() => controller.abort(), 15000);

  try {
    const data = await requestGraph(controller.signal);
    if (requestedRevision !== revision) return false;
    graph = validateGraph(data, matrix.length, matrix[0].length, start);
    frames = evolve(graph, matrix, start, Number(element('steps').value));
    element('timeline').disabled = false;
    showStatus('Python graph loaded · animating its probability distribution.');
    return true;
  } finally {
    clearTimeout(timeout);
    if (requestedRevision === revision) {
      setLoading(false);
      pendingRequest = null;
    }
  }
}

function scheduleNextStep() {
  playbackTimer = setTimeout(() => {
    if (!playing) return;
    currentStep++;
    renderFrame();
    if (currentStep === frames.length - 1) {
      pause();
      showStatus('Playback complete. Scrub the timeline or simulate again.');
    } else {
      scheduleNextStep();
    }
  }, Number(element('speed').value));
}

async function runSimulation(singleStep = false) {
  if (playing && !singleStep) {
    pause();
    return;
  }
  pause();
  const requestedRevision = revision;
  try {
    if (!await prepareSimulation()) return;
    if (currentStep === frames.length - 1) currentStep = 0;
    if (singleStep) {
      currentStep++;
      renderFrame();
      showStatus(`Paused at step ${currentStep}. Showing probabilities from the Python graph.`);
      return;
    }
    playing = true;
    showStatus('Playing the probability distribution from the Python graph.');
    document.body.classList.remove('paused');
    element('simulate').textContent = 'Ⅱ Pause';
    renderFrame();
    scheduleNextStep();
  } catch (error) {
    if (requestedRevision !== revision) return;
    const message = error.name === 'AbortError'
      ? 'API request timed out. Check that your Python server is running.'
      : error.message;
    showStatus(message, true);
  }
}

// Control handlers ----------------------------------------------------------

function resizeMatrix() {
  if (!element('rows').reportValidity() || !element('cols').reportValidity()) return;
  const rows = Number(element('rows').value);
  const columns = Number(element('cols').value);
  const resized = [];
  for (let row = 0; row < rows; row++) {
    resized[row] = [];
    for (let column = 0; column < columns; column++) {
      resized[row][column] = matrix[row]?.[column] || [0, 0];
    }
  }
  matrix = resized;
  start = [Math.min(start[0], rows - 1), Math.min(start[1], columns - 1)];
  element('example').value = 'custom';
  invalidateSimulation();
  renderMatrix();
}

function randomizeMatrix() {
  const randomPayoff = () => Math.floor(Math.random() * 15) - 5;
  for (const row of matrix) {
    for (const cell of row) {
      cell[0] = randomPayoff();
      cell[1] = randomPayoff();
    }
  }
  element('example').value = 'custom';
  invalidateSimulation('Randomized payoffs from −5 to 9. Choose a start and simulate.');
  renderMatrix();
}

function resetPlayback() {
  if (pendingRequest) {
    invalidateSimulation('Request cancelled. Returned to the initial state.');
    return;
  }
  pause();
  currentStep = 0;
  renderFrame();
  showStatus('Returned to the initial state.');
}

function bindControls() {
  element('simulate').addEventListener('click', () => runSimulation());
  element('step').addEventListener('click', () => runSimulation(true));
  element('reset').addEventListener('click', resetPlayback);
  element('resize').addEventListener('click', resizeMatrix);
  element('randomize').addEventListener('click', randomizeMatrix);
  element('show-flows').addEventListener('change', renderFlows);

  element('timeline').addEventListener('input', () => {
    pause();
    currentStep = Number(element('timeline').value);
    renderFrame();
  });
  element('example').addEventListener('change', () => {
    matrix = structuredClone(PRESETS[element('example').value]);
    start = [0, 0];
    invalidateSimulation();
    renderMatrix();
  });
  for (const id of ['rule1', 'rule2', 'steps']) {
    element(id).addEventListener('change', () => invalidateSimulation());
  }
  element('player-prob').addEventListener('input', () => {
    const probability = Number(element('player-prob').value);
    element('p1-share').textContent = `${probability}%`;
    element('p2-share').textContent = `${100 - probability}%`;
    invalidateSimulation();
  });
}

bindControls();
new ResizeObserver(renderFlows).observe(element('matrix-stage'));
renderMatrix();
pause();
