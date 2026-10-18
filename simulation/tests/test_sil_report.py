import json
import re
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from gridflex_simulation.controller_in_the_loop import ControllerInTheLoopRunner
from gridflex_simulation.scenario_catalogue import sunny_day
from gridflex_simulation.sil_report import comparison_to_dict, render_html, write_report
from tests.fake_controller import FakeController

STATUS: dict[str, Any] = {
    "status": "healthy",
    "version": "1.0.0",
    "nativeController": {
        "ready": True,
        "abiVersion": 2,
        "limits": {
            "maxChargePowerKw": 10,
            "maxDischargePowerKw": 8,
            "minimumBatterySocKwh": 2,
            "maximumBatterySocKwh": 20,
        },
    },
}


def _render(status: dict[str, Any] | None = STATUS) -> str:
    comparison = ControllerInTheLoopRunner.compare(sunny_day(), FakeController())

    return render_html(
        [comparison],
        api_url="http://localhost:5080",
        api_status=status,
        generated_at=datetime(2026, 10, 18, 12, 0, tzinfo=UTC),
    )


def test_report_is_self_contained() -> None:
    page = _render()

    assert "<script" not in page
    assert not re.search(r'(src|href)="(https?:)?//', page)
    assert page.count("<svg") == 3


def test_report_shows_the_controller_window_and_limits_when_the_api_reports_them() -> None:
    page = _render()

    assert 'class="band"' in page
    assert "native ABI 2" in page
    assert "charge ≤ 10 kW" in page


def test_report_works_without_api_status() -> None:
    page = _render(status=None)

    assert 'class="band"' not in page
    assert "<svg" in page


def test_every_point_has_a_tooltip_and_every_decision_a_row() -> None:
    page = _render()

    assert page.count("<tr><td>") == 24
    assert "<title>C++ controller · 13:00:" in page


def test_report_escapes_scenario_names() -> None:
    comparison = ControllerInTheLoopRunner.compare(sunny_day(), FakeController())
    hostile = replace(comparison, scenario=replace(comparison.scenario, name="<b>x</b>"))

    page = render_html(
        [hostile],
        api_url="http://localhost:5080",
        api_status=None,
        generated_at=datetime(2026, 10, 18, tzinfo=UTC),
    )

    assert "<b>x</b>" not in page
    assert "&lt;b&gt;x&lt;/b&gt;" in page


def test_write_report_creates_json_and_html(tmp_path: Path) -> None:
    comparison = ControllerInTheLoopRunner.compare(sunny_day(), FakeController())

    page = write_report(
        tmp_path / "report",
        [comparison],
        api_url="http://localhost:5080",
        api_status=STATUS,
    )

    assert page.name == "index.html"

    result = json.loads((tmp_path / "report" / "sunny-day.json").read_text(encoding="utf-8"))
    assert result == json.loads(json.dumps(comparison_to_dict(comparison)))
    assert result["controller"]["totals"]["consumedEnergyKwh"] > 0
