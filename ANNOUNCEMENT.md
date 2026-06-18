# LinkedIn announcement — intent-verify

"It passed" usually means "it didn't error." Those are not the same
thing, and the gap between them is where outages hide.

`intent-verify` makes verification a declarative, first-class artifact.
You write *what should be true* — the index responds on 9200, the
process runs with the new heap, the config contains the new route — and
the tool checks it and returns a three-valued verdict:

- **verified** — the signal was read and matched.
- **failed** — the signal was read and did not match.
- **inconclusive** — the signal could *not* be read (command missing,
  host unreachable). Reported honestly, never silently passed.

That third value is the one most tooling gets wrong. If you can't reach
the host, you didn't observe a failure — you failed to observe. Folding
that into "pass" is how a broken deploy gets a green check. `intent-verify`
keeps it separate, and lets you decide per context whether inconclusive
should block (strict, for CI) or not.

The mental model shift: stop writing tests that assert on incidental
side effects, and start declaring the observable end state you actually
care about. A change is done when a signal confirms it — so make the
signal the artifact.

Python, MIT. The intent spec is plain YAML; check kinds are pluggable.

Repo: github.com/qa-veritas/intent-verify

#testing #qa #sre #aiengineering #verification
