from intentverify.checks import FAILED, INCONCLUSIVE, VERIFIED, CheckOutcome
from intentverify.runner import RunReport


def _report(statuses, inconclusive_is=INCONCLUSIVE):
    outcomes = [CheckOutcome(f"c{i}", s) for i, s in enumerate(statuses)]
    return RunReport(intent="t", outcomes=outcomes, inconclusive_is=inconclusive_is)


def test_all_verified():
    assert _report([VERIFIED, VERIFIED]).verdict == VERIFIED


def test_any_failed_is_failed():
    assert _report([VERIFIED, FAILED]).verdict == FAILED


def test_inconclusive_neutral_by_default():
    assert _report([VERIFIED, INCONCLUSIVE]).verdict == INCONCLUSIVE


def test_inconclusive_strict_becomes_failed():
    assert _report([VERIFIED, INCONCLUSIVE], inconclusive_is=FAILED).verdict == FAILED


def test_inconclusive_lenient_becomes_verified():
    assert _report([VERIFIED, INCONCLUSIVE], inconclusive_is=VERIFIED).verdict == VERIFIED


def test_counts():
    counts = _report([VERIFIED, VERIFIED, FAILED, INCONCLUSIVE]).counts
    assert counts == {VERIFIED: 2, FAILED: 1, INCONCLUSIVE: 1}
