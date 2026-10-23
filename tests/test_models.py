from agent.models import ActionProposal, load_config, make_timeline_event


def test_timeline_helper():
    e = make_timeline_event("detected", at=1.0)
    assert (e.time, e.actor, e.event, e.reference_ids) == (1.0, "agent", "detected", [])


def test_config_env_only():
    c = load_config({"METRICS_URL": "http://x", "LLM_API_KEY": "secret", "BREACH_POLLS": "4"})
    assert c.metrics_url == "http://x" and c.breach_polls == 4
    assert "secret" not in repr(c)


def test_payload_hash_stable():
    a = ActionProposal("a", "t", {"x": 1, "y": 2}, "r", "e", "rb")
    b = ActionProposal("a", "t", {"y": 2, "x": 1}, "r", "e", "rb")
    assert a.compute_hash() == b.compute_hash()
