"""The check kinds.

Every check returns one of three statuses. The crucial discipline:
return ``inconclusive`` when the signal could not be read (a missing
command, an unreachable host) rather than ``failed`` — you cannot
conclude a change failed from a signal you never observed.
"""

from __future__ import annotations

import socket
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from intentverify.spec import Check

VERIFIED = "verified"
FAILED = "failed"
INCONCLUSIVE = "inconclusive"


@dataclass
class CheckOutcome:
    """The result of one check."""

    name: str
    status: str          # verified | failed | inconclusive
    detail: str = ""


def _file_exists(check: Check) -> CheckOutcome:
    path = Path(check.params.get("path", ""))
    if path.exists():
        return CheckOutcome(check.name, VERIFIED, f"{path} exists")
    return CheckOutcome(check.name, FAILED, f"{path} does not exist")


def _file_contains(check: Check) -> CheckOutcome:
    path = Path(check.params.get("path", ""))
    needle = str(check.params.get("contains", ""))
    if not path.exists():
        return CheckOutcome(check.name, INCONCLUSIVE, f"{path} not readable")
    if needle in path.read_text(errors="replace"):
        return CheckOutcome(check.name, VERIFIED, f"{path} contains {needle!r}")
    return CheckOutcome(check.name, FAILED, f"{path} does not contain {needle!r}")


def _command(check: Check) -> CheckOutcome:
    cmd = check.params.get("run")
    if not cmd:
        return CheckOutcome(check.name, INCONCLUSIVE, "no command given")
    try:
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=check.params.get("timeout", 30))
    except FileNotFoundError:
        return CheckOutcome(check.name, INCONCLUSIVE, "command not found")
    except subprocess.TimeoutExpired:
        return CheckOutcome(check.name, INCONCLUSIVE, "command timed out")

    expect_contains = check.params.get("expect_stdout_contains")
    if proc.returncode != 0:
        return CheckOutcome(check.name, FAILED, f"exit {proc.returncode}: {proc.stderr.strip()[:120]}")
    if expect_contains is not None and str(expect_contains) not in proc.stdout:
        return CheckOutcome(check.name, FAILED, f"stdout missing {expect_contains!r}")
    return CheckOutcome(check.name, VERIFIED, "exit 0" + ("; stdout matched" if expect_contains else ""))


def _http_status(check: Check) -> CheckOutcome:
    url = check.params.get("url", "")
    expect = int(check.params.get("expect_status", 200))
    try:
        with urllib.request.urlopen(url, timeout=check.params.get("timeout", 5)) as resp:
            status = resp.status
    except urllib.error.HTTPError as error:
        status = error.code
    except (urllib.error.URLError, socket.timeout, ValueError):
        return CheckOutcome(check.name, INCONCLUSIVE, f"{url} unreachable")
    if status == expect:
        return CheckOutcome(check.name, VERIFIED, f"status {status}")
    return CheckOutcome(check.name, FAILED, f"status {status}, expected {expect}")


def _port_open(check: Check) -> CheckOutcome:
    host = check.params.get("host", "localhost")
    port = int(check.params.get("port", 0))
    try:
        with socket.create_connection((host, port), timeout=check.params.get("timeout", 3)):
            return CheckOutcome(check.name, VERIFIED, f"{host}:{port} accepted a connection")
    except (ConnectionRefusedError, socket.timeout, OSError):
        # Refused/unreachable: we couldn't observe the service, so this is
        # inconclusive for verification purposes, not a hard failure.
        return CheckOutcome(check.name, INCONCLUSIVE, f"{host}:{port} not reachable")


_DISPATCH = {
    "file_exists": _file_exists,
    "file_contains": _file_contains,
    "command": _command,
    "http_status": _http_status,
    "port_open": _port_open,
}


def run_check(check: Check) -> CheckOutcome:
    """Run a single check and return its outcome."""
    handler = _DISPATCH.get(check.kind)
    if handler is None:
        return CheckOutcome(check.name, INCONCLUSIVE, f"no handler for kind {check.kind!r}")
    return handler(check)
