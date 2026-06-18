# Example prompts

How an agent uses intent-verify to make "done" observable.

## Turn an intent into checks

> The change intent is: "db-1 is serving with a 16 GB heap." Write an
> intent-verify spec whose checks would prove that: the health endpoint
> returns 200, the process reports -Xmx16g, and the transport port is
> open. Mark live checks so they're inconclusive (not failed) if the
> host is unreachable.

## Gate a CI step on verification, not "no error"

> Run `examples/intent.yaml` with `--inconclusive-is failed` in CI. I
> want the build to fail if any signal couldn't be read, because in CI
> an unreachable service is a real problem.

## Distinguish failed from inconclusive

> This run came back with one inconclusive check (port_open on 9300).
> Tell me what that means: did the change fail, or did we just fail to
> observe it? What's the next thing to check?

## Verify only what should have moved

> Before the change, snapshot the current state. After, run the intent
> spec and tell me whether exactly the things that were supposed to
> change did — and nothing else regressed.
