---
name: bugkiller
description: 'Investigate a developer-reported bug from a bug description, identify and rank likely root causes with evidence quality, write BUG_INVESTIGATION.md with ranked problems, detailed solutions, and Implemented?/Worked? status columns, then iteratively apply one selected fix at a time until the user confirms one worked or every proposed fix has failed. Use when invoked as /bugkiller or when asked to investigate and fix a bug through a ranked hypothesis document.'
---

# 🐛 Bugkiller

> **Purpose**: Read a bug description, investigate the system for likely causes, write `BUG_INVESTIGATION.md` with ranked hypotheses, evidence quality, detailed solutions, and per-solution attempt status, then iteratively implement one developer-selected fix at a time until the developer confirms one worked or every proposed solution has been tried and failed.

## Usage

```text
/bugkiller {{BUG DESCRIPTION}}
```

## Required Inputs

- A concrete bug description, including any observed behavior, expected behavior, reproduction steps, logs, screenshots, or environment details the developer provides.

If the bug description is missing, stop and ask the developer to provide it. If the description is present but ambiguous, ask only the minimum clarifying questions needed to avoid investigating the wrong behavior.

## Required Outputs

- `BUG_INVESTIGATION.md` at the repository root.
- A ranked markdown table in `BUG_INVESTIGATION.md` with exactly these columns: `Description`, `Ranking`, `Quality`, `Solution`, `Implemented?`, and `Worked?`.
- An interactive retry loop where the developer selects one eligible table row at a time.
- Status updates in `BUG_INVESTIGATION.md`: `Implemented?` is marked `🟢` after a row has been applied, and `Worked?` is marked `🟢` only after the developer confirms it fixed the bug or `🔴` after the developer confirms it did not.
- A successful implemented fix, only after the developer selects a table entry and confirms that it worked.
- An automated regression test for the successful fix that simulates the bug and should fail on the resolved base ref but pass on the fixed branch.
- A final summary for the developer explaining what happened, what changed, and how it was verified.
- After every failed or blocked attempt, a new structured question that offers the next eligible rows instead of stopping at a status summary.

## Safety Boundaries

- Keep investigation read-only except for writing `BUG_INVESTIGATION.md`; do not modify application code, tests, or configuration until the developer has selected a solution.
- Do not implement a fix before the developer selects a solution.
- Implement one independent table row at a time. Do not batch independent fixes unless the developer explicitly asks for a custom combined attempt.
- After each attempted fix, ask the developer whether it really fixed the bug before finalizing the attempt as successful.
- If an attempted fix did not work, remove only the code, test, and configuration changes made during that attempt. Keep the `BUG_INVESTIGATION.md` status marks that record the failed attempt.
- Never retry a row where `Implemented?` is `🟢` and `Worked?` is `🔴` unless the developer explicitly asks to revisit it.
- Preserve unrelated user changes in the working tree.
- Do not invent evidence. Separate confirmed facts from plausible inferences.
- Never ask the developer to paste secrets into chat.

## Loop Invariants

- The bugkiller workflow is not complete after an attempted fix fails, after an implementation is rolled back, or after a selected attempt is blocked before implementation.
- A turn that records a failed attempt must end by returning to Step 6 and asking the developer to choose the next eligible row, unless one row has `Worked?` = `🟢` or every row has `Implemented?` = `🟢` and `Worked?` = `🔴`.
- A turn that records a blocked selected attempt must end by returning to Step 6 and asking the developer to choose another eligible row or retry the blocked row after the blocker is resolved.
- Do not replace the Step 6 structured question with a normal final summary while unresolved eligible rows remain.
- Treat a developer's custom direction as a row selection when it clearly maps to an existing table row. If it does not map to an existing row, add or update a row first, then continue with the selected-row flow.
- A selected row counts as `Implemented?` = `🟢` only after its code, test, or configuration changes were actually applied. Investigation notes, command failures, unavailable tooling, or environmental blockers do not count as implementation.

## Step 1 — Capture the Bug

1. Restate the bug description in your own words.
2. Identify expected behavior, actual behavior, affected workflows, and any reproduction steps.
3. If reproduction steps are absent, infer likely entry points from the description and note that reproduction is inferred.
4. Check the working tree status so unrelated local changes are visible before investigation.
5. If the developer provided a base ref, store it as `BASE_REF` and use it for regression verification.

## Step 2 — Resolve the Base Ref

Resolve the base ref before ranking causes so regression expectations are tied to the right branch.

1. If the developer provided a base ref, verify that it exists and use it.
2. Otherwise, try this fallback chain in order:
   - `upstream/main`
   - `upstream/master`
   - `origin/main`
   - `origin/master`
3. Store the first valid ref as `BASE_REF`.
4. If none of the fallback refs exist, ask the developer which base ref to use before continuing.

Use `BASE_REF` throughout investigation notes and regression verification.

## Step 3 — Investigate in Read-Only Mode

Investigate deeply enough to produce credible ranked causes and realistic fix options.

1. Find relevant entry points, files, tests, routes, commands, jobs, components, configuration, data models, and dependencies.
2. Trace the bug path from input to failure point.
3. Look for nearby tests and existing regression coverage.
4. Reproduce the bug when practical using focused commands or tests.
5. Collect concrete evidence such as failing output, suspicious code paths, missing guards, stale assumptions, data shape mismatches, race conditions, dependency changes, or configuration gaps.

Use repository conventions and fast local search tools such as `rg` when available. Keep notes concise; they will become the basis of `BUG_INVESTIGATION.md`.

## Step 4 — Rank Likely Causes

Assign each likely cause a probability ranking:

| Ranking | Meaning |
|---------|---------|
| ⭐️⭐️⭐️⭐️⭐️ | Confirmed or nearly confirmed by reproduction, failing tests, logs, or direct code-path evidence |
| ⭐️⭐️⭐️⭐️ | Strongly likely based on multiple pieces of evidence |
| ⭐️⭐️⭐️ | Plausible and consistent with the bug, but not directly confirmed |
| ⭐️⭐️ | Possible but weakly supported |
| ⭐️ | Low-confidence fallback explanation |

Assign each likely cause an evidence quality:

| Quality | Meaning |
|---------|---------|
| `confirmed` | Reproduced directly, proven by a failing test, or established by logs or direct code-path evidence |
| `observed` | Supported by concrete local observations, but not fully reproduced end to end |
| `inferred` | Reasoned from code paths, data flow, or configuration when direct evidence is unavailable |
| `speculative` | A weak fallback explanation that fits the symptom but lacks meaningful evidence |

Do not use a high ranking with weak evidence quality. A `speculative` cause should usually be one or two stars. A five-star cause should normally be `confirmed`.

Prefer fewer, stronger hypotheses over a long speculative list. Include at least one solution for every listed cause.

## Step 5 — Write `BUG_INVESTIGATION.md`

Before writing, check whether `BUG_INVESTIGATION.md` already exists at the repository root.

- If it does not exist, create it.
- If it exists and clearly belongs to this same investigation, update it.
- If it exists and appears unrelated or you cannot tell, read it and ask the developer before replacing it.
- If an existing same-investigation table uses the legacy four-column format, migrate it to the six-column format and leave status cells blank unless the current conversation already proves a status.
- Preserve existing `Implemented?` and `Worked?` values when updating a same-investigation table unless the developer explicitly asks to reset them.

Write `BUG_INVESTIGATION.md` with this structure:

```markdown
# Bug Investigation

## Bug Description

[Original developer-provided bug description, lightly normalized for clarity.]

## Ranked Causes and Solutions

| Description | Ranking | Quality | Solution | Implemented? | Worked? |
|-------------|---------|---------|----------|--------------|---------|
| **1. [Problem description]**<br><br>[Key evidence and affected code path.] | ⭐️⭐️⭐️⭐️⭐️ | confirmed | [Detailed solution, including expected files/modules to change and why this fixes the bug.] |  |  |
| **2. [Problem description]**<br><br>[Key evidence and affected code path.] | ⭐️⭐️⭐️ | inferred | [Detailed solution, including expected files/modules to change and why this fixes the bug.] |  |  |
```

Rules for the table:

- Keep exactly six columns: `Description`, `Ranking`, `Quality`, `Solution`, `Implemented?`, and `Worked?`.
- Order rows from highest ranking to lowest ranking.
- Use only these `Quality` values: `confirmed`, `observed`, `inferred`, or `speculative`.
- Number each row inside the `Description` cell so the developer can select solutions by number.
- Leave `Implemented?` and `Worked?` blank for untried rows.
- Use only these non-blank status values in `Implemented?` and `Worked?`: `🟢` and `🔴`.
- For `Implemented?`, use blank for not attempted and `🟢` for attempted. Do not mark unattempted rows as `🔴`.
- Mark `Implemented?` as `🟢` immediately after the row's fix has been applied in the code, even if the fix is later rolled back because it did not work.
- Mark `Worked?` as `🟢` only after the developer confirms the applied fix solved the bug.
- Mark `Worked?` as `🔴` if the developer says the applied fix did not solve the bug. Keep `Implemented?` as `🟢` for that row.
- Escape pipe characters in cell content.
- Keep solutions detailed enough to implement without re-investigating from scratch.

After writing the file, summarize the top candidates and ask the developer to select one eligible row number or describe a custom direction. Use the harness's structured user-question tool when available, such as `AskUserQuestion` or an equivalent `question` tool; otherwise ask a concise normal question and wait. Do not modify code yet.

## Step 6 — Ask for the Next Fix Attempt

The developer may select one row, ask for edits to the investigation, or provide a custom direction.

- If any row has `Implemented?` = `🟢` and a blank `Worked?` value, treat it as a pending confirmation and go to Step 8 for that row before offering new choices.
- Build the choice list from eligible rows in `BUG_INVESTIGATION.md`.
- A row is eligible when both `Implemented?` and `Worked?` are blank.
- Exclude rows where `Worked?` is `🟢`; a confirmed working fix ends the loop.
- Exclude rows where `Implemented?` is `🟢` and `Worked?` is `🔴`; those attempts already failed.
- Present each option with the row number plus a brief description of the suspected cause and the proposed implementation.
- Ask the developer to pick exactly one row for the next attempt. If they select multiple independent rows, ask which one to try first.
- If they select one row, implement only that selected fix.
- If they ask for changes to the investigation, update `BUG_INVESTIGATION.md` and wait again.
- If they provide a custom direction, restate it and follow it only if it is compatible with the evidence and safety boundaries. If the custom direction is a new candidate fix, add or update a table row before implementing it.
- If the custom direction clearly matches an existing row, treat that row as selected even if the developer did not provide the row number.
- If the selection is ambiguous, ask a concise clarifying question before editing code.
- If no eligible rows remain and no row has `Worked?` = `🟢`, stop and report that every proposed fix was implemented and confirmed not to work. Ask whether the developer wants a deeper follow-up investigation with new hypotheses.
- If there are unresolved eligible rows, do not stop after reporting a failed or blocked attempt. Ask the Step 6 question in the same assistant turn.

## Step 7 — Implement the Selected Attempt

Once the developer selects the next solution:

1. Re-read the selected table row and relevant code.
2. Implement the smallest fix that addresses the selected root cause.
3. Follow existing architecture, naming, validation, error handling, and test conventions.
4. Avoid unrelated refactors.
5. Add or update an automated regression test for the selected attempt when practical. A regression test is required for the final successful fix.
6. Update `BUG_INVESTIGATION.md` so the selected row has `Implemented?` = `🟢` and `Worked?` remains blank.

Before editing application code, capture enough pre-attempt state to roll back only this attempt if it fails:

- Check the current working tree status.
- Note existing unrelated changes and do not overwrite them.
- Track the files and hunks you change for this attempt.
- Do not use destructive whole-tree rollback commands such as `git reset --hard` or broad checkout commands. If the attempt fails, manually remove or reverse only the hunks introduced by that attempt while preserving unrelated user changes and `BUG_INVESTIGATION.md` status updates.

When a selected row is applied, run the focused verification that is practical before asking the developer whether the bug is fixed. Include the local verification result in the question.

If a selected row cannot be applied because a required command, tool, credential, dependency, device, or environment is unavailable:

1. Do not mark `Implemented?` or `Worked?` for that row.
2. Remove any partial code, test, or configuration changes made for that blocked attempt while preserving unrelated user changes.
3. Add an `Attempt Notes` section to `BUG_INVESTIGATION.md`, or update the existing one, explaining the selected row, the exact blocker, and the commands or checks that proved it.
4. Keep the row eligible unless the developer explicitly removes it or confirms the blocker cannot be resolved.
5. Return immediately to Step 6 and ask the developer to choose another eligible row or retry the blocked row after resolving the blocker.

## Step 8 — Ask Whether the Attempt Worked

After applying the selected row and marking `Implemented?` as `🟢`, ask the developer whether the fix really solved the bug. Use the harness's structured user-question tool when available.

Use this prompt shape:

```text
Bugfix #[row number] ("[brief solution description]") applied.

Did it really fix the bug?
```

Choices:

| Choice | Meaning |
|--------|---------|
| Yes | The bug is fixed by this attempt |
| No | The bug still reproduces or the fix is not acceptable |

If the developer answers `Yes`:

1. Update `BUG_INVESTIGATION.md` so the selected row has `Worked?` = `🟢`.
2. Keep the implementation and regression test changes.
3. Continue to final regression verification.

If the developer answers `No`:

1. Update `BUG_INVESTIGATION.md` so the selected row has `Worked?` = `🔴` while keeping `Implemented?` = `🟢`.
2. Remove only the code, test, and configuration changes introduced by this failed attempt.
3. Preserve `BUG_INVESTIGATION.md` status updates and all unrelated working tree changes.
4. Confirm the failed attempt's code changes have been removed.
5. Return to Step 6 and ask the developer to choose another eligible row.

After a `No` response, do not end the interaction with only a rollback summary. The same assistant turn must either ask the Step 6 next-row question or state that no eligible rows remain.

Loop through Steps 6, 7, and 8 until one row has `Worked?` = `🟢` or until all rows have been attempted and confirmed not to work.

## Step 9 — Verify the Successful Regression Test

After the developer confirms that an attempt worked, run the focused regression test on the fixed branch and confirm it passes. Then verify that the same test fails against `BASE_REF`.

Preferred base-ref verification process:

1. Confirm `BASE_REF` still exists.
2. Create a temporary worktree from `BASE_REF`.
3. Apply only the regression test changes, plus any required test fixture changes, to that worktree. Do not apply the production fix.
4. Run the focused regression test in the temporary worktree and confirm it fails for the expected bug reason.
5. Remove the temporary worktree.
6. Run the focused test, and any relevant broader suite, on the fixed branch and confirm it passes.

If base-ref verification is impractical, document exactly why and report the strongest available alternative evidence, such as a focused reproduction command, logs, failing local output before the fix, or a code-path proof.

## Step 10 — Final Summary

After implementation and verification, report:

- Which `BUG_INVESTIGATION.md` row worked.
- Which rows were attempted and confirmed not to work, if any.
- The confirmed root cause.
- The files changed.
- The regression test added or updated.
- The commands run and whether they passed.
- Which `BASE_REF` was used and whether the regression test was confirmed to fail there.
- If base-ref verification was not completed, why it was impractical and what alternative evidence was used.
- Any residual risks or follow-up recommendations.
