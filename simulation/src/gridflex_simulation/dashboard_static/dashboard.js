// GridFlex energy dashboard: scenario selection, a run through the real
// controller path, interval playback and decision inspection.
//
// All data comes from the local dashboard server (/api/...), which runs the
// Python plant model against the GridFlex API. Text from the server is only
// ever inserted with textContent, never parsed as HTML.

const SVG_NS = "http://www.w3.org/2000/svg";
const WIDTH = 640;
const HEIGHT = 250;
const MARGIN = { top: 14, right: 16, bottom: 28, left: 44 };

const SERIES = {
  solar: { label: "Solar generation", color: "var(--series-solar)" },
  load: { label: "Building load", color: "var(--series-load)" },
  battery: { label: "Battery (discharge + / charge −)", color: "var(--series-battery)" },
  grid: { label: "Grid (import + / export −)", color: "var(--series-grid)" },
  unresolved: { label: "Unresolved (unserved + / curtailed −)", color: "var(--series-unresolved)" },
  controller: { label: "C++ controller", color: "var(--series-battery)" },
  reference: { label: "Python reference", color: "var(--series-reference)" },
};

const ACTION_TEXT = {
  ChargeBattery: "Charge battery",
  DischargeBattery: "Discharge battery",
  Idle: "Idle",
  ImportFromGrid: "Import from grid",
  ExportToGrid: "Export to grid",
};

const state = {
  scenarios: [],
  selected: null,
  run: null,
  index: 0,
  timer: null,
  cursors: [],
};

const $ = (id) => document.getElementById(id);

function el(tag, attributes = {}, ...children) {
  const node = document.createElement(tag);
  for (const [name, value] of Object.entries(attributes)) {
    if (name === "class") node.className = value;
    else if (name.startsWith("on")) node.addEventListener(name.slice(2), value);
    else node.setAttribute(name, value);
  }
  for (const child of children) {
    if (child === null || child === undefined) continue;
    node.append(child instanceof Node ? child : String(child));
  }
  return node;
}

function svg(tag, attributes = {}) {
  const node = document.createElementNS(SVG_NS, tag);
  for (const [name, value] of Object.entries(attributes)) node.setAttribute(name, value);
  return node;
}

const kwh = (value) => `${value.toFixed(2)} kWh`;
const kw = (value) => `${value.toFixed(2)} kW`;

function clock(hours) {
  const minutes = Math.round(hours * 60);
  return `${String(Math.floor(minutes / 60) % 24).padStart(2, "0")}:${String(minutes % 60).padStart(2, "0")}`;
}

async function getJson(url, options) {
  const response = await fetch(url, options);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.detail || body.title || `HTTP ${response.status}`);
  }
  return body;
}

// ---------------------------------------------------------------- status

async function loadControllerStatus() {
  const target = $("controller-status");
  try {
    const result = await getJson("/api/controller");
    target.replaceChildren();
    if (!result.reachable) {
      target.append(
        el("span", { class: "bad" }, "GridFlex API not reachable"),
        ` at ${result.apiUrl}. Start the backend, then reload.`,
      );
      return;
    }
    const status = result.status;
    const controller = status.nativeController || {};
    const limits = controller.limits || {};
    target.append(
      el("span", { class: status.status === "healthy" ? "ok" : "bad" }, `API ${status.status}`),
      ` · ${result.apiUrl} · native ABI ${controller.abiVersion ?? "?"} · `,
      el("strong", {}, "controller limits"),
      `: charge ≤ ${limits.maxChargePowerKw} kW, discharge ≤ ${limits.maxDischargePowerKw} kW, ` +
        `state of charge ${limits.minimumBatterySocKwh}–${limits.maximumBatterySocKwh} kWh` +
        ` · ${status.decisions?.decided ?? 0} decisions served`,
    );
  } catch (error) {
    target.replaceChildren(el("span", { class: "bad" }, "Dashboard server error"), `: ${error.message}`);
  }
}

// ------------------------------------------------------------- scenarios

async function loadScenarios() {
  state.scenarios = await getJson("/api/scenarios");
  const list = $("scenario-list");
  list.replaceChildren();
  for (const scenario of state.scenarios) {
    const facts =
      `${scenario.intervals} × ${scenario.intervalHours} h · battery ${scenario.battery.capacityKwh} kWh ` +
      `(starts ${scenario.battery.initialStateOfChargeKwh}) · load up to ${scenario.building.peakLoadKw} kW · ` +
      (scenario.grid.available ? `grid ≤ ${scenario.grid.maxImportPowerKw} kW` : "no grid");
    const button = el(
      "button",
      {
        type: "button",
        class: "scenario",
        role: "radio",
        "aria-checked": "false",
        "data-name": scenario.name,
        onclick: () => selectScenario(scenario.name),
      },
      el("strong", {}, scenario.name),
      el("span", {}, scenario.summary),
      el("span", {}, facts),
    );
    list.append(button);
  }
  const fromHash = decodeURIComponent(location.hash.slice(1));
  selectScenario(state.scenarios.some((s) => s.name === fromHash) ? fromHash : state.scenarios[0]?.name);
}

function selectScenario(name) {
  state.selected = name;
  for (const button of document.querySelectorAll(".scenario")) {
    button.setAttribute("aria-checked", String(button.dataset.name === name));
  }
  $("run-button").disabled = !name;
}

async function runSelectedScenario() {
  const name = state.selected;
  const status = $("run-status");
  const button = $("run-button");
  stopPlayback();
  button.disabled = true;
  status.className = "muted";
  status.textContent = `Running ${name}: every interval goes through the API to the C++ controller…`;
  try {
    const run = await getJson("/api/runs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario: name }),
    });
    state.run = run;
    history.replaceState(null, "", `#${encodeURIComponent(name)}`);
    const roundTrips = run.controller.steps.map((step) => step.roundTripMs);
    status.textContent =
      `${name}: ${roundTrips.length} decisions from the C++ controller in ${run.durationMs.toFixed(0)} ms ` +
      `(median round trip ${median(roundTrips).toFixed(1)} ms) · API ${run.apiVersion ?? "?"} at ${run.apiUrl}`;
    renderRun();
    loadControllerStatus();
  } catch (error) {
    status.className = "error";
    status.textContent = `The run failed: ${error.message}`;
  } finally {
    button.disabled = false;
  }
}

function median(values) {
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
}

// ---------------------------------------------------------------- charts

function niceMax(value) {
  if (value <= 0) return 1;
  const magnitude = 10 ** Math.floor(Math.log10(value));
  for (const step of [1, 2, 2.5, 5, 10]) {
    if (step * magnitude >= value) return step * magnitude;
  }
  return 10 * magnitude;
}

function ticks(min, max) {
  const span = max - min;
  const step = niceMax(span / 4);
  const values = [];
  for (let value = Math.ceil(min / step) * step; value <= max + 1e-9; value += step) values.push(value);
  return values;
}

// A chart frame: scales, gridlines, axes, hover/click targets and a cursor.
function createFrame(container, { count, yMin, yMax, label, describe }) {
  const root = svg("svg", { viewBox: `0 0 ${WIDTH} ${HEIGHT}`, role: "img", "aria-label": label });
  const innerWidth = WIDTH - MARGIN.left - MARGIN.right;
  const innerHeight = HEIGHT - MARGIN.top - MARGIN.bottom;
  const band = innerWidth / count;
  const x = (position) => MARGIN.left + position * band;
  const y = (value) => MARGIN.top + innerHeight - ((value - yMin) / (yMax - yMin)) * innerHeight;

  const axis = svg("g", { class: "axis" });
  for (const value of ticks(yMin, yMax)) {
    root.append(svg("line", { class: value === 0 ? "zero" : "gridline", x1: MARGIN.left, x2: WIDTH - MARGIN.right, y1: y(value), y2: y(value) }));
    const text = svg("text", { x: MARGIN.left - 6, y: y(value) + 4, "text-anchor": "end" });
    text.textContent = Number.isInteger(value) ? value : value.toFixed(1);
    axis.append(text);
  }
  for (let hour = 0; hour <= count; hour += Math.max(1, Math.round(count / 8))) {
    const text = svg("text", { x: x(hour), y: HEIGHT - 8, "text-anchor": "middle" });
    text.textContent = clock(state.run.controller.steps[0].intervalHours * hour);
    axis.append(text);
  }
  root.append(axis);

  const marks = svg("g");
  root.append(marks);

  const cursor = svg("line", { class: "cursor", y1: MARGIN.top, y2: HEIGHT - MARGIN.bottom });
  root.append(cursor);

  const hits = svg("g");
  for (let index = 0; index < count; index += 1) {
    const hit = svg("rect", { class: "hit", x: x(index), y: MARGIN.top, width: band, height: innerHeight });
    hit.addEventListener("mousemove", (event) => showTooltip(event, describe(index)));
    hit.addEventListener("mouseleave", hideTooltip);
    hit.addEventListener("click", () => {
      stopPlayback();
      setIndex(index);
    });
    hits.append(hit);
  }
  root.append(hits);

  container.replaceChildren(root);
  state.cursors.push((index) => {
    const position = x(index + 0.5);
    cursor.setAttribute("x1", position);
    cursor.setAttribute("x2", position);
  });

  return { marks, x, y, band };
}

function linePath(points) {
  return points.map(([px, py], i) => `${i ? "L" : "M"}${px.toFixed(1)},${py.toFixed(1)}`).join("");
}

function legend(container, entries) {
  container.replaceChildren(
    ...entries.map(([key, kind]) => {
      const swatch = el("i", { class: kind || "" });
      if (kind !== "band") swatch.style.background = SERIES[key]?.color;
      if (kind === "dash") swatch.style.borderColor = SERIES[key]?.color;
      return el("span", {}, swatch, key === "window" ? "Controller operating window" : SERIES[key].label);
    }),
  );
}

function tooltipRows(title, rows) {
  return [el("strong", {}, title), ...rows.map(([key, text]) => {
    const swatch = el("i");
    swatch.style.background = SERIES[key]?.color || "transparent";
    return el("div", { class: "row" }, swatch, text);
  })];
}

function renderFlowsChart(steps) {
  const max = niceMax(Math.max(...steps.flatMap((s) => [s.generatedEnergyKwh, s.consumedEnergyKwh])));
  const frame = createFrame($("chart-flows"), {
    count: steps.length,
    yMin: 0,
    yMax: max,
    label: "Solar generation and building load per interval",
    describe: (i) => tooltipRows(clock(steps[i].startTimeHours), [
      ["solar", `Solar ${kwh(steps[i].generatedEnergyKwh)}`],
      ["load", `Load ${kwh(steps[i].consumedEnergyKwh)}`],
      [null, `Net ${kwh(steps[i].netEnergyKwh)}`],
    ]),
  });
  for (const [key, field] of [["solar", "generatedEnergyKwh"], ["load", "consumedEnergyKwh"]]) {
    const points = steps.map((s, i) => [frame.x(i + 0.5), frame.y(s[field])]);
    frame.marks.append(svg("path", { class: "line", d: linePath(points), stroke: SERIES[key].color }));
  }
  legend($("legend-flows"), [["solar", "line"], ["load", "line"]]);
}

function flowText(name, [upLabel, up], [downLabel, down]) {
  if (up > 0) return `${upLabel} ${kwh(up)}`;
  if (down > 0) return `${downLabel} ${kwh(down)}`;
  return `${name} 0.00 kWh`;
}

function renderExchangeChart(steps) {
  const up = steps.map((s) => s.dischargedEnergyKwh + s.gridImportEnergyKwh + s.unservedEnergyKwh);
  const down = steps.map((s) => s.chargedEnergyKwh + s.gridExportEnergyKwh + s.curtailedEnergyKwh);
  const extent = niceMax(Math.max(...up, ...down));
  const frame = createFrame($("chart-exchange"), {
    count: steps.length,
    yMin: -extent,
    yMax: extent,
    label: "Battery and grid energy exchange per interval",
    describe: (i) => {
      const s = steps[i];
      return tooltipRows(`${clock(s.startTimeHours)} · ${ACTION_TEXT[s.response.action] || s.response.action}`, [
        ["battery", flowText("Battery", ["Discharged", s.dischargedEnergyKwh], ["Charged", s.chargedEnergyKwh])],
        ["grid", flowText("Grid", ["Imported", s.gridImportEnergyKwh], ["Exported", s.gridExportEnergyKwh])],
        ["unresolved", flowText("Unresolved", ["Unserved", s.unservedEnergyKwh], ["Curtailed", s.curtailedEnergyKwh])],
      ]);
    },
  });
  const barWidth = Math.max(2, frame.band - 4);
  const gap = 1; // half of the 2px surface gap between stacked segments
  steps.forEach((s, i) => {
    const left = frame.x(i) + (frame.band - barWidth) / 2;
    const stacks = [
      [["battery", s.dischargedEnergyKwh], ["grid", s.gridImportEnergyKwh], ["unresolved", s.unservedEnergyKwh]],
      [["battery", -s.chargedEnergyKwh], ["grid", -s.gridExportEnergyKwh], ["unresolved", -s.curtailedEnergyKwh]],
    ];
    for (const stack of stacks) {
      let base = 0;
      for (const [key, value] of stack) {
        if (Math.abs(value) < 1e-9) continue;
        const top = frame.y(Math.max(base, base + value));
        const bottom = frame.y(Math.min(base, base + value));
        const height = Math.max(0, bottom - top - 2 * gap);
        if (height > 0) {
          frame.marks.append(svg("rect", { x: left, y: top + gap, width: barWidth, height, rx: 2, fill: SERIES[key].color }));
        }
        base += value;
      }
    }
  });
  legend($("legend-exchange"), [["battery"], ["grid"], ["unresolved"]]);
}

function renderSocChart(run) {
  const steps = run.controller.steps;
  const reference = run.reference.steps;
  const capacity = run.referenceLimits.maximumStateOfChargeKwh;
  const frame = createFrame($("chart-soc"), {
    count: steps.length,
    yMin: 0,
    yMax: niceMax(capacity),
    label: "Battery state of charge, C++ controller compared with the Python reference",
    describe: (i) => tooltipRows(`${clock(steps[i].startTimeHours)}–${clock(steps[i].startTimeHours + steps[i].intervalHours)}`, [
      ["controller", `C++ controller ${steps[i].stateOfChargeBeforeKwh.toFixed(2)} → ${steps[i].stateOfChargeAfterKwh.toFixed(2)} kWh`],
      ["reference", `Python reference ${reference[i].stateOfChargeBeforeKwh.toFixed(2)} → ${reference[i].stateOfChargeAfterKwh.toFixed(2)} kWh`],
    ]),
  });
  const limits = run.controllerLimits;
  if (limits) {
    const top = frame.y(limits.maximumStateOfChargeKwh);
    const bottom = frame.y(limits.minimumStateOfChargeKwh);
    frame.marks.append(svg("rect", { class: "band", x: frame.x(0), y: top, width: frame.x(steps.length) - frame.x(0), height: bottom - top }));
    for (const level of [limits.minimumStateOfChargeKwh, limits.maximumStateOfChargeKwh]) {
      frame.marks.append(svg("line", { class: "band-edge", x1: frame.x(0), x2: frame.x(steps.length), y1: frame.y(level), y2: frame.y(level) }));
    }
    const text = svg("text", { class: "label", x: frame.x(0) + 4, y: bottom - 4 });
    text.textContent = `controller minimum ${limits.minimumStateOfChargeKwh} kWh`;
    frame.marks.append(text);
  }
  // State of charge is a level at interval boundaries: start, then each end.
  const series = [
    ["reference", [reference[0].stateOfChargeBeforeKwh, ...reference.map((s) => s.stateOfChargeAfterKwh)], "line dashed"],
    ["controller", [steps[0].stateOfChargeBeforeKwh, ...steps.map((s) => s.stateOfChargeAfterKwh)], "line"],
  ];
  for (const [key, values, cls] of series) {
    const points = values.map((value, i) => [frame.x(i), frame.y(value)]);
    frame.marks.append(svg("path", { class: cls, d: linePath(points), stroke: SERIES[key].color }));
  }
  const marker = svg("circle", { class: "marker", r: 5, fill: SERIES.controller.color });
  const referenceMarker = svg("circle", { class: "marker", r: 5, fill: SERIES.reference.color });
  frame.marks.append(referenceMarker, marker);
  state.cursors.push((index) => {
    marker.setAttribute("cx", frame.x(index + 1));
    marker.setAttribute("cy", frame.y(steps[index].stateOfChargeAfterKwh));
    referenceMarker.setAttribute("cx", frame.x(index + 1));
    referenceMarker.setAttribute("cy", frame.y(reference[index].stateOfChargeAfterKwh));
  });
  legend($("legend-soc"), [["controller", "line"], ["reference", "dash"], ...(limits ? [["window", "band"]] : [])]);
}

function showTooltip(event, content) {
  const tooltip = $("tooltip");
  tooltip.replaceChildren(...content);
  tooltip.hidden = false;
  const offset = 14;
  const left = Math.min(event.clientX + offset, window.innerWidth - tooltip.offsetWidth - 8);
  const top = Math.min(event.clientY + offset, window.innerHeight - tooltip.offsetHeight - 8);
  tooltip.style.left = `${Math.max(8, left)}px`;
  tooltip.style.top = `${Math.max(8, top)}px`;
}

function hideTooltip() {
  $("tooltip").hidden = true;
}

// ------------------------------------------------------------- inspector

function renderInspector(index) {
  const run = state.run;
  const step = run.controller.steps[index];
  const reference = run.reference.steps[index];
  const end = step.startTimeHours + step.intervalHours;
  $("inspector-clock").textContent = clock(step.startTimeHours);

  const decision = step.response.requestedPowerKw > 0
    ? `${ACTION_TEXT[step.response.action] || step.response.action} at ${kw(step.response.requestedPowerKw)}`
    : ACTION_TEXT[step.response.action] || step.response.action;

  const flowRows = [
    ["Charged into battery", "chargedEnergyKwh"],
    ["Discharged from battery", "dischargedEnergyKwh"],
    ["Imported from grid", "gridImportEnergyKwh"],
    ["Exported to grid", "gridExportEnergyKwh"],
    ["Curtailed (surplus lost)", "curtailedEnergyKwh"],
    ["Unserved (load not met)", "unservedEnergyKwh"],
    ["State of charge after", "stateOfChargeAfterKwh"],
  ];

  const sources = step.generatedEnergyKwh + step.dischargedEnergyKwh + step.gridImportEnergyKwh + step.unservedEnergyKwh;
  const sinks = step.consumedEnergyKwh + step.chargedEnergyKwh + step.gridExportEnergyKwh + step.curtailedEnergyKwh;
  const conserved = Math.abs(sources - sinks) < 1e-6;

  $("inspector").replaceChildren(
    el("div", { class: "decision" }, decision),
    el("div", { class: "why" }, step.explanation.text),
    el(
      "dl",
      {},
      el("dt", {}, "Interval"), el("dd", {}, `${clock(step.startTimeHours)}–${clock(end)} (step ${step.stepNumber})`),
      el("dt", {}, "Solar / load"), el("dd", {}, `${kwh(step.generatedEnergyKwh)} / ${kwh(step.consumedEnergyKwh)}`),
      el("dt", {}, "Net"), el("dd", {}, `${kwh(step.netEnergyKwh)} (${step.netEnergyKwh >= 0 ? "surplus" : "deficit"})`),
      el("dt", {}, "State of charge"), el("dd", {}, `${step.stateOfChargeBeforeKwh.toFixed(2)} → ${step.stateOfChargeAfterKwh.toFixed(2)} kWh`),
      el("dt", {}, "API round trip"), el("dd", {}, `${step.roundTripMs.toFixed(1)} ms`),
    ),
    el(
      "table",
      { class: "flows" },
      el("thead", {}, el("tr", {}, el("th", { scope: "col" }, "Applied to the simulated plant"), el("th", { scope: "col" }, "C++ controller"), el("th", { scope: "col" }, "Python reference"))),
      el("tbody", {}, ...flowRows.map(([label, field]) =>
        el("tr", {}, el("td", {}, label), el("td", {}, step[field].toFixed(2)), el("td", {}, reference[field].toFixed(2))))),
    ),
    el(
      "p",
      { class: conserved ? "check-ok" : "check-bad" },
      `${conserved ? "✓" : "✗"} Energy conserved: sources ${kwh(sources)} = sinks ${kwh(sinks)}`,
    ),
    el("details", {}, el("summary", {}, "Request sent to POST /api/control/decision"), el("pre", {}, JSON.stringify(step.request, null, 2))),
    el("details", {}, el("summary", {}, "Response from the C++ controller"), el("pre", {}, JSON.stringify(step.response, null, 2))),
  );
}

// ------------------------------------------------------------ comparison

function renderComparison(run) {
  const c = run.controller.totals;
  const r = run.reference.totals;
  const rows = [
    ["Grid import", "gridImportEnergyKwh"],
    ["Grid export", "gridExportEnergyKwh"],
    ["Charged into battery", "chargedEnergyKwh"],
    ["Discharged from battery", "dischargedEnergyKwh"],
    ["Unresolved (curtailed + unserved)", "unresolvedEnergyKwh"],
    ["Final state of charge", "finalStateOfChargeKwh"],
  ];
  $("comparison-table").replaceChildren(
    el(
      "div",
      { class: "table-wrap" },
      el(
      "table",
      {},
      el("thead", {}, el("tr", {}, el("th", { scope: "col", class: "text" }, "Totals (kWh)"), el("th", { scope: "col" }, "C++ controller"), el("th", { scope: "col" }, "Python reference"), el("th", { scope: "col" }, "Difference"))),
      el("tbody", {}, ...rows.map(([label, field]) => {
        const difference = c[field] - r[field];
        return el("tr", {}, el("td", {}, label), el("td", {}, c[field].toFixed(2)), el("td", {}, r[field].toFixed(2)),
          el("td", {}, `${difference >= 0 ? "+" : ""}${difference.toFixed(2)}`));
      })),
      ),
    ),
    el("p", { class: "muted small" }, "Difference = C++ controller − Python reference. Neither column is \"right\": they follow different limits."),
  );

  const limits = run.controllerLimits;
  const capacity = run.referenceLimits.maximumStateOfChargeKwh;
  const counts = {};
  for (const step of run.controller.steps) counts[step.explanation.code] = (counts[step.explanation.code] || 0) + 1;
  const lowestReference = Math.min(...run.reference.steps.map((s) => s.stateOfChargeAfterKwh));
  const highestReference = Math.max(...run.reference.steps.map((s) => s.stateOfChargeAfterKwh));

  const findings = [];
  const say = (code, text) => counts[code] && findings.push(`${counts[code]} interval(s): ${text}`);
  if (limits) {
    say("max-discharge-power", `discharge capped at ${limits.maxDischargePowerKw} kW, the rest imported.`);
    say("max-charge-power", `charge capped at ${limits.maxChargePowerKw} kW, the rest exported.`);
    say("soc-minimum", `discharge stopped at the ${limits.minimumStateOfChargeKwh} kWh minimum.`);
    say("battery-at-minimum", `battery held at the ${limits.minimumStateOfChargeKwh} kWh minimum, deficit imported or unserved.`);
    say("soc-maximum", `charge stopped at the ${limits.maximumStateOfChargeKwh} kWh maximum.`);
    say("battery-full", `battery full at ${limits.maximumStateOfChargeKwh} kWh, surplus exported or curtailed.`);
    if (lowestReference < limits.minimumStateOfChargeKwh - 1e-6) {
      findings.push(`The reference drains the battery to ${lowestReference.toFixed(2)} kWh, below the controller's ${limits.minimumStateOfChargeKwh} kWh protection floor.`);
    }
    if (highestReference > limits.maximumStateOfChargeKwh + 1e-6) {
      findings.push(`The reference charges to ${highestReference.toFixed(2)} kWh, above the controller's ${limits.maximumStateOfChargeKwh} kWh maximum.`);
    }
  }
  say("unexplained", "the decision does not follow from the reported limits; check the API configuration.");

  $("limits-explainer").replaceChildren(
    el("p", {}, el("strong", {}, "Why the two differ: they run under different operating limits.")),
    el(
      "ul",
      {},
      el("li", {}, el("strong", {}, "C++ controller"), limits
        ? `: charge ≤ ${limits.maxChargePowerKw} kW, discharge ≤ ${limits.maxDischargePowerKw} kW, state of charge kept between ${limits.minimumStateOfChargeKwh} and ${limits.maximumStateOfChargeKwh} kWh (limits reported by the API).`
        : ": the API did not report its limits."),
      el("li", {}, el("strong", {}, "Python reference"), `: battery-first with no power limits, and a window from 0 kWh to the full ${capacity} kWh capacity. It is a baseline for comparison, not a target: lower grid import from the reference usually means it used battery energy the controller deliberately protects.`),
    ),
    findings.length ? el("p", {}, el("strong", {}, `In ${run.scenario}:`)) : null,
    findings.length ? el("ul", {}, ...findings.map((text) => el("li", {}, text))) : null,
    el("p", { class: "muted small" }, "Both strategies run on the same Python plant model with the same grid limits; only the battery decisions differ."),
  );
}

function renderDecisionTable(run) {
  const body = $("decision-table").querySelector("tbody");
  body.replaceChildren(...run.controller.steps.map((step, index) => {
    const unresolved = step.curtailedEnergyKwh + step.unservedEnergyKwh;
    const row = el(
      "tr",
      { "data-index": String(index), onclick: () => { stopPlayback(); setIndex(index); } },
      el("td", {}, clock(step.startTimeHours)),
      el("td", {}, step.generatedEnergyKwh.toFixed(2)),
      el("td", {}, step.consumedEnergyKwh.toFixed(2)),
      el("td", {}, step.netEnergyKwh.toFixed(2)),
      el("td", { class: "text" }, step.response.action),
      el("td", {}, step.response.requestedPowerKw.toFixed(2)),
      el("td", {}, `${step.stateOfChargeBeforeKwh.toFixed(2)} → ${step.stateOfChargeAfterKwh.toFixed(2)}`),
      el("td", {}, step.gridImportEnergyKwh.toFixed(2)),
      el("td", {}, step.gridExportEnergyKwh.toFixed(2)),
      el("td", {}, unresolved.toFixed(2)),
      el("td", { class: "why-cell" }, step.explanation.text),
    );
    return row;
  }));
}

// -------------------------------------------------------------- playback

function renderRun() {
  const run = state.run;
  state.cursors = [];
  $("results").hidden = false;
  const steps = run.controller.steps;
  renderFlowsChart(steps);
  renderExchangeChart(steps);
  renderSocChart(run);
  renderComparison(run);
  renderDecisionTable(run);
  $("interval-slider").max = String(steps.length - 1);
  setIndex(0);
}

function setIndex(index) {
  const steps = state.run.controller.steps;
  state.index = Math.max(0, Math.min(steps.length - 1, index));
  for (const update of state.cursors) update(state.index);
  $("interval-slider").value = String(state.index);
  $("interval-label").textContent = clock(steps[state.index].startTimeHours);
  for (const row of $("decision-table").querySelectorAll("tbody tr")) {
    row.classList.toggle("current", row.dataset.index === String(state.index));
  }
  renderInspector(state.index);
}

function togglePlayback() {
  if (state.timer) {
    stopPlayback();
    return;
  }
  const last = state.run.controller.steps.length - 1;
  if (state.index >= last) setIndex(0);
  $("play-button").textContent = "⏸ Pause";
  $("play-button").setAttribute("aria-label", "Pause");
  const tick = () => {
    if (state.index >= last) {
      stopPlayback();
      return;
    }
    setIndex(state.index + 1);
    state.timer = setTimeout(tick, Number($("speed-select").value));
  };
  state.timer = setTimeout(tick, Number($("speed-select").value));
}

function stopPlayback() {
  clearTimeout(state.timer);
  state.timer = null;
  $("play-button").textContent = "▶ Play";
  $("play-button").setAttribute("aria-label", "Play");
}

function wireControls() {
  $("run-button").addEventListener("click", runSelectedScenario);
  $("play-button").addEventListener("click", togglePlayback);
  $("first-button").addEventListener("click", () => { stopPlayback(); setIndex(0); });
  $("previous-button").addEventListener("click", () => { stopPlayback(); setIndex(state.index - 1); });
  $("next-button").addEventListener("click", () => { stopPlayback(); setIndex(state.index + 1); });
  $("interval-slider").addEventListener("input", (event) => { stopPlayback(); setIndex(Number(event.target.value)); });
  document.addEventListener("keydown", (event) => {
    if (!state.run || event.target.closest("input, select, textarea")) return;
    // A focused button handles Space itself.
    if (event.key === " " && event.target.closest("button")) return;
    if (event.key === "ArrowRight") { stopPlayback(); setIndex(state.index + 1); event.preventDefault(); }
    if (event.key === "ArrowLeft") { stopPlayback(); setIndex(state.index - 1); event.preventDefault(); }
    if (event.key === " ") { togglePlayback(); event.preventDefault(); }
  });
}

wireControls();
loadControllerStatus();
loadScenarios().catch((error) => {
  $("run-status").className = "error";
  $("run-status").textContent = `Could not load scenarios: ${error.message}`;
});
