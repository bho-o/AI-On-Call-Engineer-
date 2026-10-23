import importlib

import pytest

MODULES = [
    "agent.detector", "agent.investigator", "agent.ledger", "agent.verifier", "agent.diagnosis",
    "agent.planner", "agent.gate", "agent.executor", "agent.postcheck", "agent.reporter", "agent.models",
    "tools.metrics", "tools.traces", "tools.logs", "tools.containers", "tools.guard",
]


@pytest.mark.parametrize("name", MODULES)
def test_module_imports(name):
    importlib.import_module(name)
