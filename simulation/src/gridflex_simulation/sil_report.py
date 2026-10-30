"""
Read-only report of software-in-the-loop runs.

Writes one JSON file per scenario and a single self-contained HTML page
(inline SVG and CSS, no scripts and no external resources) that shows, for
every scenario, the energy flows, the battery state of charge with the C++
controller compared to the Python reference strategy, the grid exchange,
and every decision in a table.
"""

import json
import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any

from gridflex_simulation.controller_in_the_loop import LoopResult, ScenarioComparison

_WIDTH = 600
_HEIGHT = 250
_LEFT = 44
_RIGHT = 104
_TOP = 28
_BOTTOM = 30


@dataclass(frozen=True)
class Series:
    label: str
    values: tuple[float, ...]
    color_variable: str


def comparison_to_dict(comparison: ScenarioComparison) -> dict[str, Any]:
    """
    Machine-readable result of one scenario.
    """

    controller = comparison.controller
    reference = comparison.reference

    return {
        "scenario": comparison.scenario.name,
        "controller": {
            "totals": loop_totals(controller),
            "steps": [
                {
                    "stepNumber": step.step_number,
                    "startTimeHours": step.start_time_hours,
                    "intervalHours": step.interval_hours,
                    "generatedEnergyKwh": step.generated_energy_kwh,
                    "consumedEnergyKwh": step.consumed_energy_kwh,
                    "netEnergyKwh": step.net_energy_kwh,
                    "stateOfChargeBeforeKwh": step.state_of_charge_before_kwh,
                    "decision": {
                        "action": step.decision.action,
                        "requestedPowerKw": step.decision.requested_power_kw,
                    },
                    "chargedEnergyKwh": step.charged_energy_kwh,
                    "dischargedEnergyKwh": step.discharged_energy_kwh,
                    "stateOfChargeAfterKwh": step.state_of_charge_after_kwh,
                    "gridImportEnergyKwh": step.grid_import_energy_kwh,
                    "gridExportEnergyKwh": step.grid_export_energy_kwh,
                    "curtailedEnergyKwh": step.curtailed_energy_kwh,
                    "unservedEnergyKwh": step.unserved_energy_kwh,
                }
                for step in controller.steps
            ],
        },
        "reference": {
            "totals": {
                "gridImportEnergyKwh": reference.total_grid_import_energy_kwh,
                "gridExportEnergyKwh": reference.total_grid_export_energy_kwh,
                "unresolvedEnergyKwh": reference.total_unresolved_energy_kwh,
                "finalStateOfChargeKwh": reference.final_battery_state_of_charge_kwh,
            },
            "stateOfChargeAfterKwh": [
                step.measurement.battery_state_of_charge_kwh for step in reference.steps
            ],
        },
    }


def loop_totals(result: LoopResult) -> dict[str, float]:
    return {
        "generatedEnergyKwh": result.total_generated_energy_kwh,
        "consumedEnergyKwh": result.total_consumed_energy_kwh,
        "chargedEnergyKwh": result.total_charged_energy_kwh,
        "dischargedEnergyKwh": result.total_discharged_energy_kwh,
        "gridImportEnergyKwh": result.total_grid_import_energy_kwh,
        "gridExportEnergyKwh": result.total_grid_export_energy_kwh,
        "unresolvedEnergyKwh": result.total_unresolved_energy_kwh,
        "finalStateOfChargeKwh": result.final_state_of_charge_kwh,
    }


def write_report(
    directory: Path,
    comparisons: Sequence[ScenarioComparison],
    *,
    api_url: str,
    api_status: dict[str, Any] | None,
    generated_at: datetime | None = None,
) -> Path:
    """
    Write ``<scenario>.json`` files and ``index.html``; return the HTML path.
    """

    directory.mkdir(parents=True, exist_ok=True)

    for comparison in comparisons:
        (directory / f"{comparison.scenario.name}.json").write_text(
            json.dumps(comparison_to_dict(comparison), indent=2) + "\n",
            encoding="utf-8",
        )

    page = directory / "index.html"
    page.write_text(
        render_html(
            comparisons,
            api_url=api_url,
            api_status=api_status,
            generated_at=generated_at or datetime.now(UTC),
        ),
        encoding="utf-8",
    )

    return page


def render_html(
    comparisons: Sequence[ScenarioComparison],
    *,
    api_url: str,
    api_status: dict[str, Any] | None,
    generated_at: datetime,
) -> str:
    limits = _controller_limits(api_status)

    sections = "\n".join(_scenario_section(comparison, limits) for comparison in comparisons)

    navigation = " · ".join(
        f'<a href="#{escape(c.scenario.name)}">{escape(c.scenario.name)}</a>' for c in comparisons
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GridFlex SIL Report</title>
<style>{_STYLE}</style>
</head>
<body>
<main class="viz-root">
<header>
<h1>GridFlex EMS: controller in the loop</h1>
<p class="lede">Each interval, the Python plant model sent its measurement to
<code>{escape(api_url)}/api/control/decision</code>. The C++ controller decided
through the ASP.NET Core API and the C ABI, and the simulation applied that
decision to the <strong>simulated</strong> battery and grid. The Python
battery-first strategy, which has no power limits and an operating window of
0&nbsp;kWh to the full capacity, runs the same scenario as a reference.</p>
{_api_summary(api_status)}
<p class="meta">Generated {escape(generated_at.strftime("%Y-%m-%d %H:%M UTC"))} ·
Scenarios: {navigation}</p>
</header>
{sections}
<footer><p class="meta">Simulation only. No electrical equipment is controlled.</p></footer>
</main>
</body>
</html>
"""


def _api_summary(status: dict[str, Any] | None) -> str:
    if not status:
        return ""

    controller = status.get("nativeController")
    parts = [
        f"API status <strong>{escape(str(status.get('status', '?')))}</strong>",
    ]

    if "version" in status:
        parts.append(f"version {escape(str(status['version']))}")

    if isinstance(controller, dict):
        parts.append(f"native ABI {escape(str(controller.get('abiVersion', '?')))}")

        limits = controller.get("limits")

        if isinstance(limits, dict):
            parts.append(
                "controller limits: charge ≤ "
                f"{_number(limits.get('maxChargePowerKw'))} kW, discharge ≤ "
                f"{_number(limits.get('maxDischargePowerKw'))} kW, state of charge "
                f"{_number(limits.get('minimumBatterySocKwh'))}–"
                f"{_number(limits.get('maximumBatterySocKwh'))} kWh"
            )

    return f'<p class="meta">{" · ".join(parts)}</p>'


def _controller_limits(status: dict[str, Any] | None) -> tuple[float, float] | None:
    """
    The controller's state-of-charge window, if the API reports it.
    """

    controller = (status or {}).get("nativeController")
    limits = controller.get("limits") if isinstance(controller, dict) else None

    if not isinstance(limits, dict):
        return None

    try:
        return (
            float(limits["minimumBatterySocKwh"]),
            float(limits["maximumBatterySocKwh"]),
        )
    except (KeyError, TypeError, ValueError):
        return None


def _scenario_section(
    comparison: ScenarioComparison,
    soc_window: tuple[float, float] | None,
) -> str:
    name = comparison.scenario.name
    controller = comparison.controller
    reference = comparison.reference
    steps = controller.steps

    hours = tuple(step.start_time_hours + step.interval_hours for step in steps)

    energy_chart = _line_chart(
        hours,
        [
            Series(
                "Solar generation",
                tuple(step.generated_energy_kwh for step in steps),
                "--series-1",
            ),
            Series(
                "Building consumption",
                tuple(step.consumed_energy_kwh for step in steps),
                "--series-2",
            ),
        ],
        unit="kWh",
    )

    soc_chart = _line_chart(
        hours,
        [
            Series(
                "C++ controller",
                tuple(step.state_of_charge_after_kwh for step in steps),
                "--series-1",
            ),
            Series(
                "Python reference",
                tuple(step.measurement.battery_state_of_charge_kwh for step in reference.steps),
                "--series-2",
            ),
        ],
        unit="kWh",
        band=soc_window,
        y_minimum=0.0,
        y_maximum=comparison.scenario.battery.capacity_kwh,
    )

    grid_chart = _bar_chart(
        hours,
        imports=tuple(step.grid_import_energy_kwh for step in steps),
        exports=tuple(step.grid_export_energy_kwh for step in steps),
    )

    summary_rows = "\n".join(
        f"<tr><th scope=row>{escape(label)}</th>"
        f"<td>{controller_value:.2f}</td><td>{reference_value:.2f}</td></tr>"
        for label, controller_value, reference_value in (
            (
                "Grid import (kWh)",
                controller.total_grid_import_energy_kwh,
                reference.total_grid_import_energy_kwh,
            ),
            (
                "Grid export (kWh)",
                controller.total_grid_export_energy_kwh,
                reference.total_grid_export_energy_kwh,
            ),
            (
                "Unresolved (kWh)",
                controller.total_unresolved_energy_kwh,
                reference.total_unresolved_energy_kwh,
            ),
            (
                "Final state of charge (kWh)",
                controller.final_state_of_charge_kwh,
                reference.final_battery_state_of_charge_kwh,
            ),
        )
    )

    step_rows = "\n".join(
        "<tr>"
        f"<td>{_clock(step.start_time_hours)}</td>"
        f"<td>{step.generated_energy_kwh:.2f}</td>"
        f"<td>{step.consumed_energy_kwh:.2f}</td>"
        f"<td>{step.net_energy_kwh:+.2f}</td>"
        f"<td>{escape(step.decision.action)}</td>"
        f"<td>{step.decision.requested_power_kw:.2f}</td>"
        f"<td>{step.state_of_charge_before_kwh:.2f} → {step.state_of_charge_after_kwh:.2f}</td>"
        f"<td>{step.grid_import_energy_kwh:.2f}</td>"
        f"<td>{step.grid_export_energy_kwh:.2f}</td>"
        f"<td>{step.curtailed_energy_kwh + step.unserved_energy_kwh:.2f}</td>"
        "</tr>"
        for step in steps
    )

    window_note = (
        f" The shaded band is the controller's operating window "
        f"({soc_window[0]:g}–{soc_window[1]:g} kWh)."
        if soc_window
        else ""
    )

    return f"""<section id="{escape(name)}">
<h2>{escape(name)}</h2>
<p class="description">{escape(_first_line(comparison))}</p>
<div class="grid">
<figure>
<figcaption>Energy per hour</figcaption>
{_legend(("Solar generation", "--series-1"), ("Building consumption", "--series-2"))}
{energy_chart}
</figure>
<figure>
<figcaption>Battery state of charge at the end of each hour</figcaption>
{_legend(("C++ controller", "--series-1"), ("Python reference", "--series-2"))}
{soc_chart}
<p class="note">Both strategies start from the same state of charge.{window_note}</p>
</figure>
<figure>
<figcaption>Grid exchange with the C++ controller</figcaption>
{_legend(("Import", "--series-2"), ("Export", "--series-1"))}
{grid_chart}
</figure>
<figure>
<figcaption>Totals over the scenario</figcaption>
<table class="summary">
<thead><tr><th></th><th scope=col>C++ controller</th>
<th scope=col>Python reference</th></tr></thead>
<tbody>
{summary_rows}
</tbody>
</table>
</figure>
</div>
<details>
<summary>All {len(steps)} decisions</summary>
<div class="table-wrap">
<table class="steps">
<thead><tr><th>Start</th><th>Solar kWh</th><th>Load kWh</th><th>Net kWh</th>
<th>Decision</th><th>kW</th><th>SoC kWh</th><th>Import</th><th>Export</th>
<th>Unresolved</th></tr></thead>
<tbody>
{step_rows}
</tbody>
</table>
</div>
</details>
</section>"""


def _first_line(comparison: ScenarioComparison) -> str:
    from gridflex_simulation.scenario_catalogue import SCENARIOS

    factory = SCENARIOS.get(comparison.scenario.name)
    documentation = (factory.__doc__ or "") if factory else ""

    return " ".join(documentation.split()) or comparison.scenario.name


def _legend(*entries: tuple[str, str]) -> str:
    items = "".join(
        f'<li><span class="swatch" style="background: var({variable})"></span>{escape(label)}</li>'
        for label, variable in entries
    )

    return f'<ul class="legend">{items}</ul>'


def _line_chart(
    hours: tuple[float, ...],
    series: Sequence[Series],
    *,
    unit: str,
    band: tuple[float, float] | None = None,
    y_minimum: float | None = None,
    y_maximum: float | None = None,
) -> str:
    values = [value for entry in series for value in entry.values]
    low = min([0.0, *values]) if y_minimum is None else y_minimum
    high = _nice_ceiling(max([*values, 0.1] if y_maximum is None else [*values, y_maximum]))

    x_of, y_of = _scales(hours, low, high)
    parts = [_grid_and_axes(hours, low, high, unit, x_of, y_of)]

    if band is not None:
        band_low, band_high = (max(band[0], low), min(band[1], high))
        parts.append(
            f'<rect class="band" x="{_LEFT}" y="{y_of(band_high):.1f}" '
            f'width="{_WIDTH - _LEFT - _RIGHT}" '
            f'height="{y_of(band_low) - y_of(band_high):.1f}"/>'
        )

    label_positions: list[float] = []

    for entry in series:
        points = " ".join(
            f"{x_of(hour):.1f},{y_of(value):.1f}"
            for hour, value in zip(hours, entry.values, strict=True)
        )

        parts.append(
            f'<polyline class="line" points="{points}" '
            f'style="stroke: var({entry.color_variable})"/>'
        )

        for hour, value in zip(hours, entry.values, strict=True):
            parts.append(
                f'<g class="point"><circle cx="{x_of(hour):.1f}" cy="{y_of(value):.1f}" '
                f'r="9" class="hit"/><circle cx="{x_of(hour):.1f}" cy="{y_of(value):.1f}" '
                f'r="4" class="dot" style="fill: var({entry.color_variable})"/>'
                f"<title>{escape(entry.label)} · {_clock(hour)}: {value:.2f} {unit}</title></g>"
            )

        # Direct label at the line end, nudged apart from earlier labels.
        label_y = y_of(entry.values[-1])

        for taken in label_positions:
            if abs(label_y - taken) < 15:
                label_y = taken + 15

        label_positions.append(label_y)

        parts.append(
            f'<text class="direct" x="{x_of(hours[-1]) + 8:.1f}" y="{label_y + 4:.1f}">'
            f"{escape(entry.label)}</text>"
        )

    return _svg(parts, f"Line chart in {unit}")


def _bar_chart(
    hours: tuple[float, ...],
    *,
    imports: tuple[float, ...],
    exports: tuple[float, ...],
) -> str:
    """
    Imports above the zero line, exports below it.
    """

    high = _nice_ceiling(max(imports)) if max(imports) > 0 else 0.0
    low = -_nice_ceiling(max(exports)) if max(exports) > 0 else 0.0

    if high == low:
        high = 1.0

    x_of, y_of = _scales(hours, low, high)
    parts = [_grid_and_axes(hours, low, high, "kWh", x_of, y_of)]

    slot = (_WIDTH - _LEFT - _RIGHT) / len(hours)
    width = max(slot - 2, 1)
    zero = y_of(0.0)

    for hour, imported, exported in zip(hours, imports, exports, strict=True):
        left = x_of(hour) - slot + 1

        for value, variable, label in (
            (imported, "--series-2", "Import"),
            (-exported, "--series-1", "Export"),
        ):
            if value == 0:
                continue

            top = min(zero, y_of(value))
            height = abs(y_of(value) - zero)

            parts.append(
                f'<g class="point"><rect x="{left:.1f}" y="{top:.1f}" width="{width:.1f}" '
                f'height="{height:.1f}" rx="2" style="fill: var({variable})"/>'
                f"<title>{label} · hour ending {_clock(hour)}: {abs(value):.2f} kWh</title></g>"
            )

    return _svg(parts, "Grid import and export per hour")


def _scales(
    hours: tuple[float, ...],
    low: float,
    high: float,
) -> tuple[Any, Any]:
    end = max(hours[-1], 1e-9)
    plot_width = _WIDTH - _LEFT - _RIGHT
    plot_height = _HEIGHT - _TOP - _BOTTOM
    span = high - low or 1.0

    def x_of(hour: float) -> float:
        return _LEFT + hour / end * plot_width

    def y_of(value: float) -> float:
        return _TOP + (high - value) / span * plot_height

    return x_of, y_of


def _grid_and_axes(
    hours: tuple[float, ...],
    low: float,
    high: float,
    unit: str,
    x_of: Any,
    y_of: Any,
) -> str:
    parts: list[str] = []
    step = _nice_step(high - low)
    value = math.ceil(low / step - 1e-9) * step

    while value <= high + 1e-9:
        y = y_of(value)
        parts.append(
            f'<line class="{"zero" if abs(value) < 1e-9 else "gridline"}" '
            f'x1="{_LEFT}" x2="{_WIDTH - _RIGHT}" y1="{y:.1f}" y2="{y:.1f}"/>'
            f'<text class="tick" x="{_LEFT - 6}" y="{y + 4:.1f}" text-anchor="end">'
            f"{value:g}</text>"
        )
        value = round(value + step, 9)

    for hour in range(0, int(hours[-1]) + 1, 3):
        parts.append(
            f'<text class="tick" x="{x_of(hour):.1f}" y="{_HEIGHT - 12}" '
            f'text-anchor="middle">{hour:02d}:00</text>'
        )

    parts.append(
        f'<text class="tick" x="{_LEFT - 6}" y="{_TOP - 14}" text-anchor="end">{unit}</text>'
    )

    return "".join(parts)


def _svg(parts: Sequence[str], label: str) -> str:
    return (
        f'<svg viewBox="0 0 {_WIDTH} {_HEIGHT}" role="img" aria-label="{escape(label)}">'
        + "".join(parts)
        + "</svg>"
    )


def _nice_step(span: float) -> float:
    for step in (0.5, 1, 2, 2.5, 5, 10, 20, 25, 50, 100):
        if span / step <= 6:
            return float(step)

    return span / 5


def _nice_ceiling(value: float) -> float:
    step = _nice_step(value)

    return max(step, -(-value // step) * step)


def _clock(hours: float) -> str:
    whole_minutes = round(hours * 60)

    return f"{whole_minutes // 60 % 24:02d}:{whole_minutes % 60:02d}"


def _number(value: object) -> str:
    return f"{value:g}" if isinstance(value, int | float) else "?"


_STYLE = """
.viz-root {
  color-scheme: light;
  --surface-0: #f4f4f2;
  --surface-1: #fcfcfb;
  --text-primary: #0b0b0b;
  --text-secondary: #52514e;
  --text-muted: #7a7974;
  --rule: #e2e1dc;
  --band: rgba(42, 120, 214, 0.08);
  --series-1: #2a78d6;
  --series-2: #eb6834;
}
@media (prefers-color-scheme: dark) {
  :root:where(:not([data-theme="light"])) .viz-root {
    color-scheme: dark;
    --surface-0: #121211;
    --surface-1: #1a1a19;
    --text-primary: #f0efec;
    --text-secondary: #c3c2b7;
    --text-muted: #8f8e86;
    --rule: #33332f;
    --band: rgba(57, 135, 229, 0.12);
    --series-1: #3987e5;
    --series-2: #d95926;
  }
}
:root[data-theme="dark"] .viz-root {
  color-scheme: dark;
  --surface-0: #121211;
  --surface-1: #1a1a19;
  --text-primary: #f0efec;
  --text-secondary: #c3c2b7;
  --text-muted: #8f8e86;
  --rule: #33332f;
  --band: rgba(57, 135, 229, 0.12);
  --series-1: #3987e5;
  --series-2: #d95926;
}
* { box-sizing: border-box; }
html, body { margin: 0; }
body { background: #f4f4f2; }
@media (prefers-color-scheme: dark) { body { background: #121211; } }
.viz-root {
  background: var(--surface-0);
  color: var(--text-primary);
  font: 15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif;
  max-width: 1200px; margin: 0 auto; padding: 24px 16px 48px;
}
h1 { font-size: 1.6rem; margin: 0 0 8px; }
h2 { font-size: 1.25rem; margin: 40px 0 4px; }
.lede { max-width: 75ch; color: var(--text-secondary); }
.meta, .note, .description { color: var(--text-muted); font-size: 0.875rem; }
code { font-size: 0.85em; }
a { color: var(--series-1); }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 520px), 1fr));
  gap: 16px; }
figure { margin: 0; background: var(--surface-1); border: 1px solid var(--rule);
  border-radius: 8px; padding: 16px; min-width: 0; }
figcaption { font-weight: 600; margin-bottom: 4px; }
.legend { list-style: none; display: flex; flex-wrap: wrap; gap: 4px 16px; margin: 0 0 4px;
  padding: 0; color: var(--text-secondary); font-size: 0.85rem; }
.swatch { display: inline-block; width: 10px; height: 10px; border-radius: 2px;
  margin-right: 6px; vertical-align: baseline; }
svg { width: 100%; height: auto; display: block; overflow: visible; }
.gridline { stroke: var(--rule); stroke-width: 1; }
.zero { stroke: var(--text-muted); stroke-width: 1; }
.tick { fill: var(--text-muted); font-size: 12px; }
.direct { fill: var(--text-secondary); font-size: 12px; }
.line { fill: none; stroke-width: 2; stroke-linejoin: round; stroke-linecap: round; }
.dot { stroke: var(--surface-1); stroke-width: 2; }
.hit { fill: transparent; }
.band { fill: var(--band); }
.point:hover .dot { r: 5; }
.point:hover rect { opacity: 0.8; }
table { border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums; }
th, td { padding: 4px 8px; text-align: right; border-bottom: 1px solid var(--rule); }
th:first-child, td:first-child { text-align: left; }
thead th { color: var(--text-secondary); font-weight: 600; }
details { margin-top: 16px; }
summary { cursor: pointer; color: var(--text-secondary); }
.table-wrap { overflow-x: auto; }
.steps { font-size: 0.85rem; white-space: nowrap; }
"""
