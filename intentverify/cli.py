"""Command-line entrypoint for intent-verify.

Subcommand:
    run    run an intent spec and print per-check verdicts
"""

from __future__ import annotations

import argparse

from intentverify.checks import FAILED, INCONCLUSIVE, VERIFIED
from intentverify.runner import run_spec
from intentverify.spec import SpecError, load_spec

_GLYPH = {VERIFIED: "verified    ", FAILED: "FAILED      ", INCONCLUSIVE: "inconclusive"}


def cmd_run(args: argparse.Namespace) -> int:
    spec = load_spec(args.spec)
    report = run_spec(spec, inconclusive_is=args.inconclusive_is)

    if report.intent:
        print(f"intent: {report.intent}\n")
    for outcome in report.outcomes:
        print(f"  {_GLYPH.get(outcome.status, outcome.status)}  {outcome.name:30} {outcome.detail}")

    counts = report.counts
    print(
        f"\nverdict: {report.verdict.upper()}  "
        f"({counts[VERIFIED]} verified, {counts[FAILED]} failed, {counts[INCONCLUSIVE]} inconclusive)"
    )
    return 0 if report.verdict == VERIFIED else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="intentverify", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="run an intent spec")
    p_run.add_argument("--spec", required=True)
    p_run.add_argument(
        "--inconclusive-is",
        choices=[VERIFIED, FAILED, INCONCLUSIVE],
        default=INCONCLUSIVE,
        dest="inconclusive_is",
        help="how an inconclusive check affects the overall verdict",
    )
    p_run.set_defaults(func=cmd_run)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except SpecError as error:
        print(f"error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
