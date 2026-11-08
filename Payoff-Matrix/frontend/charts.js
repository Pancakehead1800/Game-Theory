// SVG drawing only. Game rules and playback controls belong elsewhere.
const PLAYER_COLORS = ['#60A5FA', '#A78BFA'];

function svgElement(tag, attributes) {
  const element = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for (const [name, value] of Object.entries(attributes)) {
    element.setAttribute(name, value);
  }
  return element;
}

function drawArrow(svg, from, to, probability, player) {
  const color = PLAYER_COLORS[player];
  const dx = to[0] - from[0];
  const dy = to[1] - from[1];
  const length = Math.hypot(dx, dy);
  const unitX = dx / length;
  const unitY = dy / length;
  const endX = to[0] - unitX * 18;
  const endY = to[1] - unitY * 18;
  const bend = player === 0 ? 10 : -10;
  const middleX = (from[0] + endX) / 2 + bend;
  const middleY = (from[1] + endY) / 2 + bend;

  svg.append(svgElement('path', {
    d: `M ${from[0]} ${from[1]} Q ${middleX} ${middleY} ${endX} ${endY}`,
    fill: 'none',
    stroke: color,
    'stroke-width': 1 + 5 * Math.sqrt(probability),
    opacity: 0.35 + 0.6 * Math.sqrt(probability),
    class: 'flow',
  }));
  svg.append(svgElement('path', {
    d: `M ${endX} ${endY}
        l ${-unitX * 7 - unitY * 4} ${-unitY * 7 + unitX * 4}
        l ${unitY * 8} ${-unitX * 8} Z`,
    fill: color,
  }));
}

export function drawFlows(flows, visible) {
  const svg = document.getElementById('flows');
  svg.replaceChildren();
  if (!flows || !visible) return;

  const bounds = document.getElementById('matrix-stage').getBoundingClientRect();
  svg.setAttribute('viewBox', `0 0 ${bounds.width} ${bounds.height}`);
  const centers = Array.from(document.querySelectorAll('.cell'), cell => {
    const box = cell.getBoundingClientRect();
    return [box.x - bounds.x + box.width / 2, box.y - bounds.y + box.height / 2];
  });

  // Python supplies the visible flows and their probability amounts.
  for (const flow of flows) {
    drawArrow(svg, centers[flow.source], centers[flow.target], flow.amount, flow.player);
  }
}

export function drawPayoffChart(frames, currentStep) {
  const svg = document.getElementById('chart');
  svg.replaceChildren();
  const values = frames.flatMap(frame => frame.utilities);
  const minimum = Math.min(0, ...values);
  const maximum = Math.max(1, ...values);
  const range = maximum - minimum;
  const lastStep = frames.length - 1;
  const x = step => 48 + step / Math.max(1, lastStep) * 832;
  const y = payoff => 120 - (payoff - minimum) / range * 104;

  for (let line = 0; line < 3; line++) {
    const payoff = minimum + range * line / 2;
    svg.append(svgElement('line', {
      x1: 48, y1: y(payoff), x2: 880, y2: y(payoff), stroke: '#252D49',
    }));
    const label = svgElement('text', {
      x: 0, y: y(payoff) + 4, fill: '#A3A3AA', 'font-size': 10,
    });
    label.textContent = payoff.toFixed(1);
    svg.append(label);
  }

  for (let player = 0; player < 2; player++) {
    const points = [];
    for (let step = 0; step <= currentStep; step++) {
      points.push(`${x(step)},${y(frames[step].utilities[player])}`);
    }
    svg.append(svgElement('polyline', {
      points: points.join(' '), fill: 'none',
      stroke: PLAYER_COLORS[player], 'stroke-width': 2,
    }));
    svg.append(svgElement('circle', {
      cx: x(currentStep), cy: y(frames[currentStep].utilities[player]),
      r: 3, fill: PLAYER_COLORS[player],
    }));
  }

  for (const [left, text] of [[48, '0'], [850, `Step ${lastStep}`]]) {
    const label = svgElement('text', {
      x: left, y: 145, fill: '#A3A3AA', 'font-size': 10,
    });
    label.textContent = text;
    svg.append(label);
  }
}
