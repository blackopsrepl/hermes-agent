---
name: verify-real-artifact
description: "Verifies changes by running the real artifact, not stubs."
version: 1.0.0
author: Vittorio Distefano (blackopsrepl), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [testing, verification, e2e, quality, evidence]
    category: software-development
    related_skills: [systematic-debugging, requesting-code-review, spike]
---

# Verify Real Artifact

Default verification policy for agent-written code. Verifies correctness by
running the real artifact end to end; unit tests are a targeted localization
and regression instrument, not the default proof. Replaces test-first
ceremony, which optimizes for a human's design discipline rather than an
agent's actual failure modes (declaring done on green unit tests while the
feature is broken end to end; mock-heavy tests that verify the mock).

## When to Use

- Verifying any feature, fix, refactor, or generated code before calling it done.
- Deciding what tests a change needs (default: none up front; targeted after).
- Bug fixes (the one mandatory test-first case, see below).
- Don't use for: exploratory spikes before the design settles — verify the
  sketch by running it, then apply this policy once it becomes real code.

## The policy

**Default verification is the real artifact.** Run the actual thing: the CLI
command, the server, the generated app, the wizard, the benchmark. A claim of
done without a real-artifact run is invalid, no matter how many unit tests
pass. Unit tests and `curl` smoke checks say nothing about whether the feature
works for its user; observed agent behavior confirms features die in the
seams between units, exactly where unit-test-green evidence is blind.

**Bug fixes keep failing-test-first.** Reproduce before fixing; the failing
repro lands in git history before the fix. This is debugging discipline, not
ritual — the repro proves the actual mechanism was fixed and gives the
reviewer an ordered, checkable history.

**Unit tests only when they earn their place:**

- Pure complex logic whose edge states are impractical to reach through a real
  run (parsers, score calculators, constraint qualification boundaries).
- Regression pins at the exact failure site — clone counters, purity checks,
  state-transition assertions. These localize a failure an e2e run can only
  announce.

**Banned:**

- Mock-heavy unit tests. A test that verifies the mock verifies nothing.
- Tests restating the signature or the compiler's work. If the test would
  still pass with every imported function returning a default, delete it.
- Test-first ceremony for greenfield code whose design is still moving.
- Writing a whole test file before any implementation (horizontal slicing).

## Procedure

1. **Build the change.** No test debt required up front.
2. **Run the real artifact** at the layer the change touches, end to end.
   Completion criterion: observed output of the real run attached to the
   claim (pasted output, exit code, screenshot — not a summary).
3. **If the e2e run fails,** drop to the unit level at the suspect seam to
   localize, fix, then re-verify at the e2e level. Both levels green before
   done. E2E announces; units localize.
4. **Add regression pins only where the failure or edge states justify them**
   (the two cases above). Each pin states the exact expected value, not a
   property that survives any implementation.
5. **Bug fixes:** failing repro first (commit or staged), then fix, then the
   repro passes on the same surface that failed.
6. **Report evidence with labels:** measured / inferred / guess. A green suite
   is not a performance verdict — speedup or cost claims need their measured
   battery (see `benchmark-checklist`-style differential runs) as part of done.

## Pitfalls

- **Verification theater:** running the happy path and calling it verified.
  Error states, restarts, and empty inputs are part of the real artifact.
- **Mock creep:** a "unit test" that stubs everything except the function
  under test proves the stubs compile.
- **Coverage as a goal:** exercised lines are not verified behavior; an
  assertion on the exact expected output is.
- **Scope creep in the repro:** the regression pin tests the fixed behavior,
  not the whole subsystem.
- **Retiring the proof:** never delete the behavioral test that caught a real
  defect to make a diff look smaller.

## Verification

Done when: the real artifact ran with its output on record; any bug fix shows
the failing repro before the fix in history; every added unit test names one
of the two justifying cases; the full existing suite still passes.

## Relation to strict TDD

This policy replaces test-first-by-default. Strict RED-GREEN-REFACTOR remains
available when the operator explicitly asks for it. The two overlap on bug
fixes (repro first) and disagree elsewhere; when an operator or project
convention mandates strict TDD, theirs wins for that work — record the
override in the task notes.
