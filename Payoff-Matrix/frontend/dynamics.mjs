// Python decides which moves are possible. This module validates that graph
// and turns it into probability distributions for the animation.

function stateIndex(state, columns) {
  return state[0] * columns + state[1];
}

function isValidState(state, rows, columns) {
  if (!Array.isArray(state) || state.length !== 2) return false;
  const [row, column] = state;
  return Number.isInteger(row) && Number.isInteger(column) &&
    row >= 0 && row < rows && column >= 0 && column < columns;
}

export function validateGraph(response, rows, columns, start) {
  if (!Array.isArray(response?.nodes)) {
    throw new Error('API response must contain a "nodes" array.');
  }

  const graph = new Map();
  for (const [index, node] of response.nodes.entries()) {
    const label = `nodes[${index}]`;
    if (!isValidState(node?.state, rows, columns)) {
      throw new Error(`${label}.state must be a valid zero-based [row, column].`);
    }
    if (!Array.isArray(node.edges)) {
      throw new Error(`${label}.edges is missing or not an array. Group each state's moves inside an "edges" list.`);
    }

    const source = stateIndex(node.state, columns);
    if (graph.has(source)) {
      throw new Error(`${label}: duplicate state [${node.state}]. Return one node per state.`);
    }

    let totalProbability = 0;
    for (const [edgeIndex, edge] of node.edges.entries()) {
      const edgeLabel = `${label}.edges[${edgeIndex}]`;
      if (!isValidState(edge?.target, rows, columns)) {
        throw new Error(`${edgeLabel}.target must be a valid [row, column].`);
      }
      if (edge.player !== 0 && edge.player !== 1) {
        throw new Error(`${edgeLabel}.player must be 0 or 1.`);
      }
      if (!Number.isFinite(edge.probability) || edge.probability < 0 || edge.probability > 1) {
        throw new Error(`${edgeLabel}.probability must be a finite number from 0 to 1.`);
      }

      // P1 changes rows (index 0); P2 changes columns (index 1).
      const unchangedCoordinate = 1 - edge.player;
      if (edge.target[unchangedCoordinate] !== node.state[unchangedCoordinate]) {
        throw new Error(`${edgeLabel} changes the other player's action.`);
      }
      totalProbability += edge.probability;
    }

    if (Math.abs(totalProbability - 1) > 1e-8) {
      throw new Error(`State [${node.state}] has outgoing probability ${totalProbability.toFixed(4)}, not 1. Include self-loops and small probabilities.`);
    }
    graph.set(source, node.edges);
  }

  if (!graph.has(stateIndex(start, columns))) {
    throw new Error(`Graph is missing the starting state [${start}].`);
  }
  for (const edges of graph.values()) {
    for (const edge of edges) {
      if (edge.probability > 0 && !graph.has(stateIndex(edge.target, columns))) {
        throw new Error(`Graph is missing destination state [${edge.target}].`);
      }
    }
  }
  return graph;
}

function expectedPayoffs(matrix, probabilities) {
  const columns = matrix[0].length;
  const utilities = [0, 0];
  for (const [index, probability] of probabilities.entries()) {
    const row = Math.floor(index / columns);
    const column = index % columns;
    utilities[0] += probability * matrix[row][column][0];
    utilities[1] += probability * matrix[row][column][1];
  }
  return utilities;
}

export function evolve(graph, matrix, start, steps) {
  const columns = matrix[0].length;
  let probabilities = Array(matrix.length * columns).fill(0);
  probabilities[stateIndex(start, columns)] = 1;
  const frames = [];

  for (let step = 0; step <= steps; step++) {
    frames.push({
      mass: probabilities,
      utilities: expectedPayoffs(matrix, probabilities),
    });
    if (step === steps) break;

    const next = Array(probabilities.length).fill(0);
    for (const [source, probability] of probabilities.entries()) {
      if (probability === 0) continue;
      for (const edge of graph.get(source)) {
        const target = stateIndex(edge.target, columns);
        next[target] += probability * edge.probability;
      }
    }
    probabilities = next;
  }
  return frames;
}
