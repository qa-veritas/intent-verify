"""Load and validate an intent spec.

A spec is an ``intent`` string plus a list of ``checks``. Each check is a
``kind`` and the fields that kind needs. Validation is structural — it
confirms the shape, not whether the targets are reachable (that's the
runner's job).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

KNOWN_KINDS = frozenset(
    {"file_exists", "file_contains", "command", "http_status", "port_open"}
)


class SpecError(ValueError):
    """Raised when an intent spec is malformed."""


@dataclass
class Check:
    """One declarative check from the spec."""

    name: str
    kind: str
    params: dict = field(default_factory=dict)


@dataclass
class IntentSpec:
    """A parsed intent spec."""

    intent: str
    checks: list[Check] = field(default_factory=list)


def load_spec(path: str | Path) -> IntentSpec:
    """Load and validate an intent spec from YAML.

    Raises:
        SpecError: If the file is missing, has no checks, or a check
            lacks a name or uses an unknown kind.
    """
    path = Path(path)
    if not path.exists():
        raise SpecError(f"no spec at {path}")

    data = yaml.safe_load(path.read_text()) or {}
    raw_checks = data.get("checks")
    if not raw_checks:
        raise SpecError("spec has no checks")

    checks: list[Check] = []
    for raw in raw_checks:
        name = raw.get("name")
        kind = raw.get("kind")
        if not name:
            raise SpecError(f"check missing a name: {raw}")
        if kind not in KNOWN_KINDS:
            raise SpecError(f"check {name!r} has unknown kind {kind!r}; known: {sorted(KNOWN_KINDS)}")
        params = {k: v for k, v in raw.items() if k not in {"name", "kind"}}
        checks.append(Check(name=name, kind=kind, params=params))

    return IntentSpec(intent=str(data.get("intent", "")), checks=checks)
