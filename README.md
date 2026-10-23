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
python -m agent.detector --mock                     # runs without the live demo
python -m agent.detector                            # live; needs METRICS_URL + queries in .env
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
