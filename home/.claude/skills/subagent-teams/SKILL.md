---
name: subagent-teams
description: Orchestrate substantial implementation work as a dual-model subagent team (Claude + Codex Sol) where the top-level agent manages rather than implements — dual independent planning, consolidation into one critical-path plan, shortest-path parallel implementation with competitive de-risking, and per-step review gates by architect/senior-MLE/researcher personas in both model families. Use for multi-file features, ticket close-outs, migrations, or any implementation big enough to warrant a plan and a review gate. NOT for single-file edits or quick fixes.
metadata:
  short-description: Dual-model (Claude + Codex Sol) plan/implement/review orchestration
---

# subagent-teams

## Role

The top-level agent is the orchestrator/manager. It plans, consolidates, delegates, reviews, and lands work. It does NOT implement directly — every code change is produced by a subagent and passes a review gate before it lands. Use Codex Sol liberally at every phase: planning, implementation, and review.

## 1. Dual planning

For each unit of work, produce two independent plans:
- One from Claude (the orchestrator itself, or a Fable planning subagent for depth).
- One from Codex Sol xhigh: `codex exec -m gpt-5.6-sol -c model_reasoning_effort="xhigh" --sandbox read-only "<brief>"`.

Give both the same written brief: the ticket's aims, the repo path, the constraints, and the deliverable shape (numbered stages, each independently landable and testable with rollback; file lists; a risk register). Tell each planner to ground every claim in file:line evidence it actually read.

## 2. Consolidate

Comb through both plans and merge them into one best, most complete plan. Spot-check each plan's load-bearing file:line claims against the repo first — a plan built on a wrong claim loses regardless of prose. Adjudicate every disagreement explicitly with a repo-grounded reason; never average. Delegate the consolidation to a fresh subagent when the plans are long (it reads both plus the brief, verifies claims, and writes a self-contained merged plan). Structure the result as a critical-path graph of semantically meaningful steps.

## 3. Implement (shortest-path, parallel, de-risked)

Walk the critical path. Parallelise every step with no dependency between them; isolate parallel implementers in their own git worktrees so they cannot collide (`Agent` with `isolation: "worktree"`, or `codex exec --sandbox workspace-write` run inside a dedicated worktree). De-risk high-complexity steps or known blockers by assigning higher seniority or by running two implementations competitively and having a reviewer pick the winner.

Seniority nomination per step (pick the model tier to the work):
- Sonnet — routine mechanical work.
- Opus — standard implementation.
- Fable — complex, critical, or judgment-heavy work.
- Codex Sol high — the second model at Fable/Opus level (`model_reasoning_effort="high"`); Codex Sol xhigh for the hardest planning/review.

Competitive step: two implementations of the same step (one Claude, one Codex Sol), a reviewer picks the superior diff; only the winner lands on the ticket branch.

## 4. Review gate (per step)

Each semantically meaningful step is reviewed before it lands. Draw reviewers from the three personas — architect, senior MLE, researcher — and run them in BOTH model families: the Claude custom agents (`architect-reviewer`, `senior-mle-reviewer`, `researcher-reviewer`) and Codex Sol xhigh with the equivalent persona prompt. Scale the reviewer count to step risk:
- Mechanical step: one persona.
- Full ticket completion: all three personas in both families (six reviews).

Fix findings the reviewers confirm; verify their claims against the code rather than trusting them. Reviewers run read-only.

## 5. Artifacts

Plans, appraisals, competing drafts, and review reports go to the session scratchpad. Only reviewed winners land in the repo. Keep one commit per landed step with a message describing what changed and why.

## Budget note

Claude subagents (the `Agent` tool) and the Bash safety classifier bill against the Anthropic org limit; `codex exec` bills separately. When the Anthropic budget is constrained, shift implementers and reviewers to Codex Sol (high ≈ Fable, medium ≈ Opus; xhigh for review), keep the orchestrator on the available Claude model, and do winner-selection in the main loop instead of spawning a Claude reviewer.
