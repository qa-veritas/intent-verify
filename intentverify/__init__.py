"""intent-verify: declare desired state; verify it with observable checks.

A change is done when an observable signal confirms it. This package
turns a declarative intent spec into checks that report verified,
failed, or inconclusive — never "probably fine."
"""

from intentverify.checks import CheckOutcome, run_check
from intentverify.runner import RunReport, run_spec
from intentverify.spec import Check, load_spec

__all__ = [
    "Check",
    "CheckOutcome",
    "RunReport",
    "load_spec",
    "run_check",
    "run_spec",
]

__version__ = "0.1.0"
