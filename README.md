# AI-On-Call-Engineer : AGENT WORKFLOW

An AI on-call engineer for the OpenTelemetry Demo (Astronomy Shop): detect -> investigate (telemetry only) -> diagnose -> propose fix -> human approval -> act -> verify -> report.

## Setup
```
python -m venv .venv && .venv\Scripts\activate    # Windows; use source .venv/bin/activate elsewhere
pip install -r requirements.txt
copy .env.example .env                              # fill in locally, never commit
```

## Run / test
```
python -m pytest -q
python -m agent.detector --mock                     # synthetic data, no live demo (prints 3 incidents)
python -m agent.detector --dry-run                  # live Prometheus, detect + print, no investigator hand-off
python -m agent.detector                            # live, hands incidents to agent.investigator.investigate(incident)
```
Detector needs `METRICS_URL` and the PromQL queries in `.env` (see `.env.example`). Tunables: `BREACH_POLLS`, `COOLDOWN_S`, `SIGMA_K`, `ABS_FLOOR`, `BASELINE_WINDOW`.
The detector polls (no alert webhook exists in the repo). Investigator must implement `investigate(incident) -> Diagnosis`; call `Detector.close(incident, status)` when an incident ends.
```
```

## Folder map
| Path | Purpose | Owner |
|---|---|---|
| agent/models.py | Shared dataclasses + env config loader | P1 |
| agent/detector.py | Polling anomaly detector, opens incidents | P1 |
| tools/metrics.py traces.py logs.py containers.py | Read-only telemetry tools | P2 |
| agent/investigator.py diagnosis.py | Hypothesis loop, diagnosis | P3 |
| agent/ledger.py verifier.py, tools/guard.py | Evidence ledger, claim verification, output guard | P4 |
| agent/planner.py gate.py executor.py postcheck.py reporter.py | Action path + report | P5 |
| tests/ docs/ eval/ reports/ | Tests, docs, eval matrix, generated reports | all |

## Branch / merge rules
- One branch per person (`person<N>/<topic>`), small PRs, **P1 merges**.
- Import shared types from `agent/models.py`. Do not edit another person's files; ask for a model change instead.
- Only the executor (P5) may call the Action API, and only after human approval.
- Diagnosis uses telemetry only. Never read flagd files/UI/API. No secrets in code, commits, logs or reports.

## Approval gate / kill switch / dry-run (P5 fills in)
TODO(P5): approval gate docs.
TODO(P5): kill switch docs.
TODO(P5): dry-run docs.
