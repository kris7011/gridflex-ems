"""INTEGRATION BRANCH ONLY (not part of any PR)."""
"""Checks that a SIL report reflects its own JSON results (and, optionally, the API status)."""
import collections, json, math, pathlib, sys, urllib.request

directory = pathlib.Path(sys.argv[1])
api = sys.argv[2] if len(sys.argv) > 2 else None
html = (directory / "index.html").read_text(encoding="utf-8")
actions = collections.Counter()
problems = []

for path in sorted(directory.glob("*.json")):
    result = json.loads(path.read_text(encoding="utf-8"))
    steps = result["controller"]["steps"]
    totals = result["controller"]["totals"]
    actions.update(step["decision"]["action"] for step in steps)
    for key, field in (("gridImportEnergyKwh", "gridImportEnergyKwh"), ("gridExportEnergyKwh", "gridExportEnergyKwh")):
        if not math.isclose(sum(s[field] for s in steps), totals[key], abs_tol=1e-9):
            problems.append(f"{path.name}: {key} total does not match its steps")
    if f"<td>{totals['gridImportEnergyKwh']:.2f}</td>" not in html:
        problems.append(f"{path.name}: grid import total not shown in index.html")
    if html.count(f'id="{result["scenario"]}"') != 1:
        problems.append(f"{path.name}: scenario section missing in index.html")
    print(f"{result['scenario']:<13} steps={len(steps)} import={totals['gridImportEnergyKwh']:.2f} "
          f"export={totals['gridExportEnergyKwh']:.2f} unresolved={totals['unresolvedEnergyKwh']:.2f}")

print("actions from JSON:", dict(actions))

if api:
    status = json.load(urllib.request.urlopen(f"{api}/api/system/status"))
    decisions = status["decisions"]
    print("status:", status["status"], "abi", status["nativeController"]["abiVersion"], "decisions", decisions["decided"])
    expected = {"Idle": actions["Idle"], "ChargeBattery": actions["ChargeBattery"], "DischargeBattery": actions["DischargeBattery"]}
    if any(decisions["decidedByAction"][k] < v for k, v in expected.items()):
        problems.append(f"status counts {decisions['decidedByAction']} are below the report's {expected}")
    if status["status"] != "healthy" or status["nativeController"]["abiVersion"] != 2 or decisions["rejected"] or decisions["failed"]:
        problems.append("status is not healthy/ABI 2 or has rejected/failed decisions")

if "native ABI 2" not in html or 'class="band"' not in html:
    problems.append("report does not show the API's ABI version and controller window")

print("\n".join(problems) or "report consistent")
sys.exit(1 if problems else 0)
