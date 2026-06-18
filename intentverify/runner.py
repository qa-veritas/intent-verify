"""Run an intent spec's checks and aggregate the verdict."""

from __future__ import annotations

from dataclasses import dataclass, field

from intentverify.checks import FAILED, INCONCLUSIVE, VERIFIED, CheckOutcome, run_check
from intentverify.spec import IntentSpec


@dataclass
class RunReport:
    """The aggregate result of running a spec."""

    intent: str
    outcomes: list[CheckOutcome] = field(default_factory=list)
    inconclusive_is: str = INCONCLUSIVE  # how to treat inconclusive in the verdict

    @property
    def counts(self) -> dict[str, int]:
        tally = {VERIFIED: 0, FAILED: 0, INCONCLUSIVE: 0}
        for outcome in self.outcomes:
            tally[outcome.status] = tally.get(outcome.status, 0) + 1
        return tally

    @property
    def verdict(self) -> str:
        """Overall verdict.

        ``failed`` if any check failed (or any inconclusive when the
        caller chose to treat inconclusive as failed); ``inconclusive``
        if any check is inconclusive and the caller left it neutral;
        otherwise ``verified``.
        """
        counts = self.counts
        effective_failed = counts[FAILED]
        if self.inconclusive_is == FAILED:
            effective_failed += counts[INCONCLUSIVE]
        if effective_failed:
            return FAILED
        if counts[INCONCLUSIVE] and self.inconclusive_is != VERIFIED:
            return INCONCLUSIVE
        return VERIFIED


def run_spec(spec: IntentSpec, inconclusive_is: str = INCONCLUSIVE) -> RunReport:
    """Run every check in a spec and build a report.

    Args:
        spec: The parsed intent spec.
        inconclusive_is: How an inconclusive check affects the verdict:
            ``inconclusive`` (default), ``failed`` (strict), or
            ``verified`` (lenient).
    """
    outcomes = [run_check(check) for check in spec.checks]
    return RunReport(intent=spec.intent, outcomes=outcomes, inconclusive_is=inconclusive_is)
