import { drawFlows, drawPayoffChart } from './charts.js';
import { setupDamping } from './damping.js?v=damping-2';

const element = id => document.getElementById(id);
let examples = new Map();
let catalogReady = false;
// Editing and playback only: all computed results arrive from Python.
let matrix = [[[0, 0]]];
let start = [0, 0];
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
  element('simulate').disabled = loading || !catalogReady;
  element('step').disabled = loading || !catalogReady;
}

function initialFrame() {
  const mass = Array(matrix.length * matrix[0].length).fill(0);
  mass[start[0] * matrix[0].length + start[1]] = 1;
  return { mass, utilities: matrix[start[0]][start[1]], most_likely: start[0] * matrix[0].length + start[1], maximum: 1, ties: 1, flows: [] };
}

function invalidateSimulation(message = 'Ready. Choose a starting cell, then simulate.') {
  // Ignore responses for an older matrix if the user edits during a request.
  revision++;
  pendingRequest?.abort();
  pendingRequest = null;
  pause();
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
  drawFlows(frames[currentStep]?.flows, element('show-flows').checked);
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

  const { maximum, most_likely: mostLikely, ties } = frame;
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
  getDamping();
  const inputs = [...document.querySelectorAll('.utility'), element('steps')];
  for (const input of inputs) {
    if (!input.checkValidity()) {
      input.reportValidity();
      throw new Error('Enter valid payoffs (−1,000,000 to 1,000,000) and 1–200 steps.');
    }
  }
}

// One HTTP helper for the three endpoints. Backend errors may be plain text.
async function request(path, { data, signal } = {}) {
  const response = await fetch(path, {
    method: data === undefined ? 'GET' : 'POST',
    headers: data === undefined ? {} : { 'Content-Type': 'application/json' },
    body: data === undefined ? undefined : JSON.stringify(data),
    signal,
    cache: 'no-store',
  });
  const text = await response.text();
  let result;
  try { result = JSON.parse(text); } catch { /* Report HTTP failures below. */ }
  if (!response.ok) throw new Error(apiError(result, response.status, path));
  if (!result) throw new Error(`${path} did not return JSON. Open this page through api.py.`);
  return result;
}

function requestSimulation(signal) {
  const playerProbability = Number(element('player-prob').value) / 100;
  return request('/api/simulate', { signal, data: {
    matrix, start,
    players: [playerProbability, 1 - playerProbability],
    rules: [element('rule1').value, element('rule2').value],
    damping: getDamping(),
    steps: Number(element('steps').value),
  }});
}

async function prepareSimulation() {
  validateInputs();
  if (frames.length) return true;

  const requestedRevision = revision;
  const controller = new AbortController();
  pendingRequest = controller;
  setLoading(true);
  showStatus('Computing simulation in Python…');
  const timeout = setTimeout(() => controller.abort(), 15000);

  try {
    const data = await requestSimulation(controller.signal);
    if (requestedRevision !== revision) return false;
    if (!Array.isArray(data.frames) || data.frames.length !== Number(element('steps').value) + 1) {
      throw new Error('The server returned an incomplete simulation. Restart api.py and reload.');
    }
    frames = data.frames;
    element('timeline').disabled = false;
    showStatus('Simulation ready · playing results from Python.');
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
      showStatus(`Paused at step ${currentStep}. Showing probabilities computed by Python.`);
      return;
    }
    playing = true;
    showStatus('Playing the probability distribution computed by Python.');
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

function apiError(data, status, path) {
  if (typeof data?.detail === 'string') return data.detail;
  if (Array.isArray(data?.detail)) return data.detail.map(error => error.msg).join(' ');
  return `${path} failed (HTTP ${status}). Check the traceback in your Python terminal.`;
}

async function randomizeMatrix() {
  if (matrix.length < 2 || matrix[0].length < 2) {
    showStatus('The random API needs at least 2 rows and 2 columns. Resize first.', true);
    return;
  }
  invalidateSimulation('Generating a random game…');
  const requestedRevision = revision;
  const controller = new AbortController();
  pendingRequest = controller;
  setLoading(true);
  element('randomize').disabled = true;
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const data = await request('/api/randomize', {
      signal: controller.signal,
      data: { m: matrix.length, n: matrix[0].length,
        lower_bound: -10, upper_bound: 10,
        seed: crypto.getRandomValues(new Uint32Array(1))[0] % 1_000_001 },
    });
    if (requestedRevision !== revision) return;
    if (!Array.isArray(data.matrix) || !Array.isArray(data.rules) || data.rules.length !== 2 ||
        data.rules.some(rule => ![...element('rule1').options].some(option => option.value === rule))) {
      throw new Error('Random API must return a matrix and two registered rule IDs.');
    }
    matrix = data.matrix;
    start = data.start;
    element('rule1').value = data.rules[0];
    element('rule2').value = data.rules[1];
    element('player-prob').value = data.players[0] * 100;
    updatePlayerLabels();
    element('damping-value').value = data.damping;
    element('damping-value').dispatchEvent(new Event('input'));
    element('example').value = 'custom';
    renderMatrix();
    showStatus('Random game loaded: payoffs, turn chances, rules and damping.');
  } catch (error) {
    if (requestedRevision === revision) showStatus(error.name === 'AbortError'
      ? 'Random game request timed out. Try again.' : error.message, true);
  } finally {
    clearTimeout(timeout);
    if (pendingRequest === controller) {
      pendingRequest = null;
      setLoading(false);
    }
    element('randomize').disabled = false;
  }
}

function updatePlayerLabels() {
  const probability = Number(element('player-prob').value);
  element('p1-share').textContent = `${Number(probability.toFixed(4))}%`;
  element('p2-share').textContent = `${Number((100 - probability).toFixed(4))}%`;
}

async function loadCatalog() {
  setLoading(true);
  element('example').disabled = true;
  element('randomize').disabled = true;
  const requestedRevision = revision;
  element('retry-catalog').hidden = true;
  showStatus('Loading examples and decision rules…');
  try {
    const data = await request('/api/catalog', { signal: AbortSignal.timeout(15000) });
    if (!Array.isArray(data.examples) || !Array.isArray(data.rules) || !data.rules.length) {
      throw new Error('The catalog needs examples and at least one decision rule.');
    }
    examples = new Map(data.examples.map(example => [example.id, example.matrix]));
    element('example').replaceChildren(new Option('Custom matrix', 'custom'));
    element('example').firstChild.disabled = true;
    for (const example of data.examples) {
      element('example').add(new Option(example.label, example.id));
    }
    for (const id of ['rule1', 'rule2']) {
      element(id).replaceChildren(...data.rules.map(rule => new Option(rule.label, rule.id)));
      if (data.rules.some(rule => rule.id === 'uniform_best')) element(id).value = 'uniform_best';
      element(id).disabled = false;
    }
    catalogReady = true;
    if (requestedRevision === revision && data.examples.length) {
      element('example').value = data.examples[0].id;
      matrix = structuredClone(data.examples[0].matrix);
      renderMatrix();
    } else {
      element('example').value = 'custom';
    }
    showStatus('Ready. Choose a starting cell, then simulate.');
  } catch (error) {
    element('retry-catalog').hidden = false;
    showStatus(`Could not load examples and rules. ${error.message}`, true);
  } finally {
    setLoading(false);
    element('example').disabled = !catalogReady;
    element('randomize').disabled = !catalogReady;
  }
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
  element('retry-catalog').addEventListener('click', loadCatalog);
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
    matrix = structuredClone(examples.get(element('example').value));
    start = [0, 0];
    invalidateSimulation();
    renderMatrix();
  });
  for (const id of ['rule1', 'rule2']) {
    element(id).addEventListener('change', () => invalidateSimulation());
  }
  element('steps').addEventListener('input', () => invalidateSimulation());
  element('player-prob').addEventListener('input', () => {
    updatePlayerLabels();
    invalidateSimulation();
  });
}

const getDamping = setupDamping(() => {
  invalidateSimulation('Damping changed. Simulate again to update the distribution.');
});
bindControls();
new ResizeObserver(renderFlows).observe(element('matrix-stage'));
renderMatrix();
pause();

loadCatalog();
