from agent.detector import Detector, MockClient
from agent.models import Config


class Seq:
    def __init__(self, values, series="error_rate"):
        self.values, self.series, self.i = values, series, 0

    def fetch(self):
        v = self.values[min(self.i, len(self.values) - 1)]
        self.i += 1
        return {self.series: v}


class Clock:
    t = 1000.0

    def __call__(self):
        return self.t


def make(values, handed=None):
    cfg = Config(min_baseline=10, breach_polls=3, cooldown_s=100)
    clk = Clock()
    det = Detector(Seq(values), cfg, on_incident=(handed.append if handed is not None else None), clock=clk)
    return det, clk


def run(det, n):
    out = []
    for _ in range(n):
        out += det.poll_once()
    return out


HEALTHY = [0.01, 0.012, 0.011, 0.009, 0.01] * 6


def test_no_alert_on_healthy_series():
    det, _ = make(HEALTHY)
    assert run(det, 30) == []


def test_alert_on_sustained_spike():
    det, _ = make(HEALTHY[:15] + [0.5] * 10)
    inc = run(det, 25)
    assert len(inc) == 1 and inc[0].symptom == "error_rate"


def test_no_alert_on_single_poll_blip():
    det, _ = make(HEALTHY[:15] + [0.5] + HEALTHY[:10])
    assert run(det, 26) == []


def test_blip_shorter_than_n_does_not_alert():
    det, _ = make(HEALTHY[:15] + [0.5, 0.5] + HEALTHY[:10])
    assert run(det, 27) == []


def test_unseen_scale_still_triggers_via_baseline():
    det, _ = make([5.0, 5.1, 4.9, 5.0, 5.05] * 3 + [9.0] * 5)  # series with its own scale
    assert len(run(det, 20)) == 1


def test_dedup_and_cooldown():
    handed = []
    det, clk = make(HEALTHY[:15] + [0.5] * 60, handed)
    assert len(run(det, 30)) == 1  # one open incident per symptom
    det.close(handed[0])
    clk.t += 10
    assert run(det, 5) == []  # inside cooldown
    clk.t += 200
    assert len(run(det, 5)) == 1  # cooldown elapsed, still breaching -> new incident


def test_status_transitions():
    handed = []
    det, _ = make(HEALTHY[:15] + [0.5] * 5, handed)
    run(det, 20)
    inc = handed[0]
    assert inc.status == "investigating"
    assert [e.actor for e in inc.timeline] == ["agent", "agent"]
    det.close(inc, "resolved")
    assert inc.status == "resolved" and inc.symptom not in det.open


def test_no_handoff_leaves_detecting():
    det, _ = make(HEALTHY[:15] + [0.5] * 5)
    assert run(det, 20)[0].status == "detecting"


def test_client_failure_does_not_crash_or_alert():
    class Boom:
        def fetch(self):
            raise OSError("down")

    assert Detector(Boom(), Config()).poll_once() == []


def test_mock_client_end_to_end():
    det = Detector(MockClient(20), Config(), clock=Clock())
    assert any(i.symptom == "error_rate" for _ in range(40) for i in det.poll_once())
