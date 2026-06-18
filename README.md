# intent-verify

[![ci](https://github.com/qa-veritas/intent-verify/actions/workflows/ci.yml/badge.svg)](https://github.com/qa-veritas/intent-verify/actions/workflows/ci.yml)

**Declare the desired state as intent; let the tool turn it into
observable checks, run them, and tell you `verified`, `failed`, or
`inconclusive` — never "probably fine."**

A change is not done when it's applied. It's done when an observable
signal confirms it. `intent-verify` makes that signal a first-class,
declarative artifact: you write *what should be true* (the index
responds on 9200, the process runs with the new heap, the config
contains the new route), and the tool checks it and reports a verdict
with evidence.

The three-valued verdict matters. Most "it passed" checks are really
"it didn't error," which is not the same as "it worked." `intent-verify`
distinguishes:

- **verified** — the signal was read and matched.
- **failed** — the signal was read and did *not* match.
- **inconclusive** — the signal could not be read (command missing,
  host unreachable). Reported honestly, never silently passed.

## Install

```bash
pip install -e .
python -m intentverify --help
```

Python 3.10+. Runtime dependency: `pyyaml`.

## Use

```bash
# Run an intent spec and print per-check verdicts
python -m intentverify run --spec examples/intent.yaml

# Non-zero exit if anything failed (CI-friendly); inconclusive is
# configurable as pass or fail
python -m intentverify run --spec examples/intent.yaml --inconclusive-is failed
```

## Writing intent

An intent spec is a list of named checks. Each declares a `kind`, a
target, and what to `expect`:

```yaml
intent: "index node db-1 is serving with the new heap"
checks:
  - name: readme present
    kind: file_exists
    path: README.md

  - name: package identity
    kind: file_contains
    path: pyproject.toml
    contains: "intent-verify"

  - name: interpreter sane
    kind: command
    run: "python3 -c 'print(42)'"
    expect_stdout_contains: "42"

  # signals that touch a live system degrade to inconclusive when the
  # target can't be reached, instead of failing the run misleadingly
  - name: index responds
    kind: http_status
    url: "http://localhost:9200/_cluster/health"
    expect_status: 200

  - name: transport port open
    kind: port_open
    host: localhost
    port: 9300
```

## Check kinds

| kind | reads | verified when |
|------|-------|---------------|
| `file_exists` | filesystem | the path exists |
| `file_contains` | filesystem | the file contains the substring |
| `command` | a subprocess | exit 0 (and optional stdout match) |
| `http_status` | a URL | the response status matches |
| `port_open` | a TCP connect | the port accepts a connection |

`http_status` and `port_open` return **inconclusive** (not failed) when
the host is unreachable — you can't conclude a change failed from a
signal you couldn't read.

## Layout

```
intent-verify/
  intentverify/
    __init__.py
    spec.py      # load + validate an intent spec into Check objects
    checks.py    # the check kinds; each returns verified/failed/inconclusive
    runner.py    # run checks, aggregate the verdict
    cli.py       # run
  examples/
    intent.yaml      # a runnable spec (verifies this repo + optional live checks)
    prompts.md
  tests/
  LICENSE
  pyproject.toml
```

## Roadmap

- A `feasibility` block per intent (pre-checks) so a change is gated
  before it's attempted, mirroring resource-ledger's capacity check.
- Retry-with-timeout on observable state (wait for green) instead of a
  single sample — no fixed sleeps.
- A `diff` mode that snapshots state before and after a change and
  verifies only what was supposed to move.
- Pluggable check kinds via entry points.

## License

MIT. See [LICENSE](LICENSE).
