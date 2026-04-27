---
name: investigator
description: 'Investigate a developer-reported bug from a bug description, identify and rank likely root causes, write BUG_INVESTIGATION.md with ranked problems and detailed solutions, wait for the user to select one or more solutions, then implement the selected fixes with regression tests. Use when invoked as /investigator or when asked to investigate and fix a bug through a ranked hypothesis document.'
---

# 🕵🏻‍♂️ Investigador

> **Purpose**: Read a bug description, investigate the system for likely causes, write `BUG_INVESTIGATION.md` with ranked hypotheses and detailed solutions, wait for the developer to choose one or more solutions, then implement the selected fix or fixes with an automated regression test.

## Usage

```text
/investigator {{BUG DESCRIPTION}}
```

## Required Inputs

- A concrete bug description, including any observed behavior, expected behavior, reproduction steps, logs, screenshots, or environment details the developer provides.

If the bug description is missing, stop and ask the developer to provide it. If the description is present but ambiguous, ask only the minimum clarifying questions needed to avoid investigating the wrong behavior.

## Required Outputs

- `BUG_INVESTIGATION.md` at the repository root.
- A ranked markdown table in `BUG_INVESTIGATION.md` with exactly these columns: `Description`, `Ranking`, and `Solution`.
- One or more implemented fixes, only after the developer selects table entries.
- An automated regression test that simulates the bug and should fail on `upstream/main` but pass on the fixed branch.
- A final summary for the developer explaining what happened, what changed, and how it was verified.

## Safety Boundaries

- Keep investigation read-only except for writing `BUG_INVESTIGATION.md`; do not modify application code, tests, or configuration until the developer has selected one or more solutions.
- Do not implement a fix before the developer selects a solution.
- Preserve unrelated user changes in the working tree.
- Do not invent evidence. Separate confirmed facts from plausible inferences.
- Never ask the developer to paste secrets into chat.

## Step 1 — Capture the Bug

1. Restate the bug description in your own words.
2. Identify expected behavior, actual behavior, affected workflows, and any reproduction steps.
3. If reproduction steps are absent, infer likely entry points from the description and note that reproduction is inferred.
4. Check the working tree status so unrelated local changes are visible before investigation.

## Step 2 — Investigate in Read-Only Mode

Investigate enough of the system to produce credible ranked causes.

1. Find relevant entry points, files, tests, routes, commands, jobs, components, configuration, data models, and dependencies.
2. Trace the bug path from input to failure point.
3. Look for nearby tests and existing regression coverage.
4. Reproduce the bug when practical using focused commands or tests.
5. Collect concrete evidence such as failing output, suspicious code paths, missing guards, stale assumptions, data shape mismatches, race conditions, dependency changes, or configuration gaps.

Use repository conventions and fast local search tools such as `rg` when available. Keep notes concise; they will become the basis of `BUG_INVESTIGATION.md`.

## Step 3 — Rank Likely Causes

Assign each likely cause a probability ranking:

| Ranking | Meaning |
|---------|---------|
| ⭐️⭐️⭐️⭐️⭐️ | Confirmed or nearly confirmed by reproduction, failing tests, logs, or direct code-path evidence |
| ⭐️⭐️⭐️⭐️ | Strongly likely based on multiple pieces of evidence |
| ⭐️⭐️⭐️ | Plausible and consistent with the bug, but not directly confirmed |
| ⭐️⭐️ | Possible but weakly supported |
| ⭐️ | Low-confidence fallback explanation |

Prefer fewer, stronger hypotheses over a long speculative list. Include at least one solution for every listed cause.

## Step 4 — Write `BUG_INVESTIGATION.md`

Create or replace `BUG_INVESTIGATION.md` at the repository root with this structure:

```markdown
# Bug Investigation

## Bug Description

[Original developer-provided bug description, lightly normalized for clarity.]

## Ranked Causes and Solutions

| Description | Ranking | Solution |
|-------------|---------|----------|
| **1. [Problem description]**<br><br>[Key evidence and affected code path.] | ⭐️⭐️⭐️⭐️⭐️ | [Detailed solution, including expected files/modules to change and why this fixes the bug.] |
| **2. [Problem description]**<br><br>[Key evidence and affected code path.] | ⭐️⭐️⭐️ | [Detailed solution, including expected files/modules to change and why this fixes the bug.] |
```

Rules for the table:

- Keep exactly three columns: `Description`, `Ranking`, and `Solution`.
- Order rows from highest ranking to lowest ranking.
- Number each row inside the `Description` cell so the developer can select solutions by number.
- Escape pipe characters in cell content.
- Keep solutions detailed enough to implement without re-investigating from scratch.

After writing the file, summarize the top candidates and explicitly wait for the developer to select one or more row numbers or describe a custom combination. Do not modify code yet.

## Step 5 — Wait for Developer Selection

The developer may select one solution, multiple solutions, ask for edits to the investigation, or provide a custom direction.

- If they select one or more rows, implement only those selected fixes.
- If they ask for changes to the investigation, update `BUG_INVESTIGATION.md` and wait again.
- If they provide a custom direction, restate it and follow it if it is compatible with the evidence and safety boundaries.
- If the selection is ambiguous, ask a concise clarifying question before editing code.

## Step 6 — Implement the Selected Fixes

Once the developer selects the solution or solutions:

1. Re-read the selected table rows and relevant code.
2. Implement the smallest fix that addresses the selected root cause.
3. Follow existing architecture, naming, validation, error handling, and test conventions.
4. Avoid unrelated refactors.
5. Add or update an automated regression test that reproduces the reported bug before the fix and passes after the fix.

When multiple solutions are selected, apply them in dependency order and keep each change traceable to the selected row.

## Step 7 — Verify the Regression Test

Run the focused regression test on the fixed branch and confirm it passes. Then verify that the same test fails against `upstream/main`.

Preferred upstream verification process:

1. Confirm `upstream/main` exists. If it does not exist, stop and ask whether to use another base branch.
2. Create a temporary worktree from `upstream/main`.
3. Apply only the regression test changes, plus any required test fixture changes, to that worktree. Do not apply the production fix.
4. Run the focused regression test in the temporary worktree and confirm it fails for the expected bug reason.
5. Remove the temporary worktree.
6. Run the focused test, and any relevant broader suite, on the fixed branch and confirm it passes.

If upstream verification is impractical, explain exactly why and report the strongest available alternative evidence.

## Step 8 — Final Summary

After implementation and verification, report:

- Which `BUG_INVESTIGATION.md` row or rows were selected.
- The confirmed root cause.
- The files changed.
- The regression test added or updated.
- The commands run and whether they passed.
- Whether the regression test was confirmed to fail on `upstream/main`.
- Any residual risks or follow-up recommendations.
