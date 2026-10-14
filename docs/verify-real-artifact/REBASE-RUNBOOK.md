# REBASE RUNBOOK — docs/verify-real-artifact

This fork branch carries ONE commit replacing the bundled TDD skill with
verify-real-artifact. Footprint: 7 skill files repointed, TDD skill deleted,
docs pages regenerated. No source code (agent/, tools/) is touched.

## Update sequence

```bash
cd /home/pvd/hermes-agent-wt-verify-docs
git fetch origin main
git rebase origin/main          # rerere replays any previously resolved conflict
bash scripts/run_tests.sh tests/skills/test_authoring_standards.py \
     tests/skills/test_verify_real_artifact_skill.py -q
git push fork --force-with-lease
```

## Failure cases and their handling

1. **Clean apply (most updates).** No overlap with upstream; rebase succeeds
   silently. Verify the test suite, push, done.

2. **Same-line conflict (rebase stops).** rerere does NOT help the first
   occurrence of a conflict shape. Read both sides, then:
   - Upstream rewrote the section for its own reasons → resolve in upstream's
     favor for their edit, re-apply our repoint (`verify-real-artifact`) on
     top of their new wording.
   - Upstream replaced test-driven-development with their own new skill →
     the premise of this branch is dead. STOP: do not re-apply. Open the PR
     and let upstream decide; drop or shrink the local commit.
   - Record the resolution and let rerere replay it next time.

3. **Structural failure (cherry-pick/rebase cannot map the patch).** Upstream
   reorganized skills/ or the docs generator. Do not force it. Re-author from
   the SKILL.md prose in `skills/software-development/verify-real-artifact/`
   — the policy text is the durable artifact; its anchoring files are not.

4. **Upstream reintroduces test-driven-development** (restores the skill or
   creates a same-shaped one). Rebase would silently resurrect our deletion
   on top of their restoration — auto-winning a policy fight. STOP after any
   rebase: `command grep -rn "test-driven-development" skills/ | head -3`.
   If it returned hits that upstream authored (check `git log origin/main --
   <file>`), stop and re-decide. Do not push.

## Hard rule

Never auto-push after a rebase that stopped for any reason. Human or agent
judgment resolves case 2 and 4; only case 1 pushes directly.