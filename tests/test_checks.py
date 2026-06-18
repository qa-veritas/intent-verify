from intentverify.checks import FAILED, INCONCLUSIVE, VERIFIED, run_check
from intentverify.spec import Check


def test_file_exists_verified(tmp_path):
    target = tmp_path / "x.txt"
    target.write_text("hi")
    outcome = run_check(Check("present", "file_exists", {"path": str(target)}))
    assert outcome.status == VERIFIED


def test_file_exists_failed(tmp_path):
    outcome = run_check(Check("absent", "file_exists", {"path": str(tmp_path / "nope")}))
    assert outcome.status == FAILED


def test_file_contains(tmp_path):
    target = tmp_path / "c.txt"
    target.write_text("the heap is 16g")
    assert run_check(Check("c", "file_contains", {"path": str(target), "contains": "16g"})).status == VERIFIED
    assert run_check(Check("c", "file_contains", {"path": str(target), "contains": "32g"})).status == FAILED


def test_command_exit_and_stdout():
    ok = run_check(Check("cmd", "command", {"run": "python3 -c 'print(42)'", "expect_stdout_contains": "42"}))
    assert ok.status == VERIFIED
    bad = run_check(Check("cmd", "command", {"run": "python3 -c 'import sys; sys.exit(3)'"}))
    assert bad.status == FAILED


def test_unreachable_port_is_inconclusive_not_failed():
    # Port 1 is essentially never accepting local connections.
    outcome = run_check(Check("p", "port_open", {"host": "localhost", "port": 1, "timeout": 1}))
    assert outcome.status == INCONCLUSIVE


def test_unreachable_http_is_inconclusive():
    outcome = run_check(
        Check("h", "http_status", {"url": "http://localhost:1/nope", "timeout": 1})
    )
    assert outcome.status == INCONCLUSIVE
