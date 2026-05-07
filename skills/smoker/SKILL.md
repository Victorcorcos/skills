---
name: smoker
description: 'Analyze the current branch diff against an explicit `BASE_REF` and generate a `SMOKE_TEST.md` file with branch-specific manual testing steps. Include prerequisite data setup using `rails c` when the change depends on database state, or API requests when the repo is frontend-only but still needs seeded backend data. Use when asked for a smoke test guide, manual QA checklist, or step-by-step branch testing instructions for a feature or bugfix.'
---

# 🚬 Smoker

> **Purpose**: Analyze the current branch diff and generate a `SMOKE_TEST.md` file that helps a developer manually verify the feature or bugfix implemented on this branch.

**Default mode**: Write `SMOKE_TEST.md` at the repository root. Do not commit it unless the user asks.

**Read-only mode**: If the user explicitly asks for analysis only, provide the proposed smoke test plan without writing the file.

---

## Input

| Parameter  | Required | Default | Description |
|------------|----------|---------|-------------|
| `BASE_REF` | Yes      | —       | Base ref to diff against. In slash-style environments, pass it as the first argument: `/smoker upstream/main`. |

If the user does not provide `BASE_REF`, stop and ask for it.

---

## Step 1 — Read The Change Surface

Inspect the branch before writing anything:

```bash
git diff "$BASE_REF" --stat
git diff "$BASE_REF" --name-only
git diff "$BASE_REF"
```

Then read the changed files that define user-visible behavior, such as:

- controllers, routes, serializers, service objects
- UI components, pages, templates, copy, and feature flags
- automated tests that reveal intended flows, edge cases, and regressions
- docs or pull request files already present in the branch

The goal is to infer how a human should exercise the change, not to restate the diff.

---

## Step 2 — Identify What Must Be Manually Verified

Extract the smallest set of user-observable scenarios that prove the branch works:

1. Cover the main happy path first.
2. Add regression checks for the bug or failure mode being fixed.
3. Add only the edge cases that are directly implied by the diff or tests.
4. If the branch contains multiple unrelated user-facing changes, group them into separate scenarios.
5. If no user-visible behavior changed, do not invent a smoke test. Write a short `SMOKE_TEST.md` explaining that the change is not meaningfully smoke-testable and list the minimal sanity checks that still make sense.

Prefer concrete actions and observable outcomes over internal implementation details.

---

## Step 3 — Determine Pre-Requisites

Add a `## Pre-requisites` section only when the tester needs a specific data state, feature flag, account type, background condition, or external record to exercise the change.

### When `rails c` is available

Prefer `rails c` commands when the repository clearly supports it and the scenario depends on database state.

Rules:

- Provide copy-pastable Ruby commands that the developer can run in `rails c`.
- Use real application models and services that exist in the codebase.
- Keep setup minimal and focused on the scenario under test.
- Make commands idempotent when reasonably possible.
- After each command block, explain in 1-2 short sentences why the setup is required.

### When `rails c` is not available

If the repository is frontend-only, or the intended workflow clearly depends on backend data that cannot be prepared through `rails c`, provide API requests instead.

Rules:

- Use project-appropriate requests via `curl`.
- When a `curl` command returns JSON, append `| jq` so the response is formatted for easier manual verification in `SMOKE_TEST.md`.
- Include placeholders for host, auth token, IDs, or environment values when needed.
- Explain what data the request creates or modifies and why the tester needs it.
- Do not assume direct database access when the project does not expose it.

Never execute the setup yourself. The skill only documents the setup.

---

## Step 4 — Write `SMOKE_TEST.md`

Create `SMOKE_TEST.md` at the repository root using this structure:

````md
# Smoke Test

## Summary
1-3 sentences explaining what changed and what the smoke test validates.

## Pre-requisites
Only include this section when setup is required.

### 1. <setup name>
Run in `rails c`:
```ruby
# copy-pastable setup
```

Why this is needed: <short explanation>

### 2. <api setup name>
Run in your terminal:
```bash
# copy-pastable setup
```

Why this is needed: <short explanation>

## Test Steps

### Scenario 1 — <happy path>
1. <action>
   Expected: <observable result>
2. <action>
   Expected: <observable result>

### Scenario 2 — <bugfix or regression check>
1. <action>
   Expected: <observable result>
````

Authoring rules:

- Use numbered steps for every scenario.
- Keep the instructions specific to this branch.
- Pair each meaningful action with an explicit expected result.
- If a test step uses `curl` and expects JSON output, include `| jq` at the end of the command.
- Start every fenced code block in `SMOKE_TEST.md` at column 1 with no leading spaces before ```` ```ruby ```` or ```` ```bash ````.
- Inside fenced code blocks, format commands with normal code indentation using two spaces where nested structure improves readability.
- For heredocs and similar shell constructs, keep the opening and closing markers aligned with the command structure, and indent nested JSON or command content by two spaces when appropriate.
- Prefer UI language the tester will actually see in the product.
- Mention routes, buttons, fields, filters, and record state only when they are grounded in the diff.
- Keep the file concise, but complete enough that a different developer can run it without reverse-engineering the branch.
- Do not add speculative scenarios that are not supported by the implementation.

### Code Block Readability

Code blocks must be readable by a human reviewer at first glance. Never inline complex payloads, chained queries, or multi-statement scripts as one-liners. Apply the following patterns whenever they fit.

#### GraphQL requests via `curl`

Do **not** embed the GraphQL operation as an escaped JSON string inside the `curl` body. Define the operation in a multi-line heredoc variable with a `GRAPHQL` delimiter, then build the JSON payload with `jq` and pipe it to `curl`. This preserves the natural indentation of the mutation/query and avoids escape-quote noise.

Use the **quoted** delimiter `<<'GRAPHQL'` for static operations so `$`, backticks, and other shell metacharacters stay literal (important for things like passwords containing `$$` and mention syntax like `@[...]`/`@@[...]`):

```bash
CREATE_QUERY=$(cat <<'GRAPHQL'
mutation {
  createRecord(
    data: {
      sheetId: "<sheet_id>"
      projectId: "<project_id>"
      dynamicFields: {
        rich_text: "<p>Tag @[<user_id>]</p>"
      }
    }
  ) {
    id
    dynamicFields
  }
}
GRAPHQL
)
CREATE_RESPONSE=$(jq -n --arg query "$CREATE_QUERY" '{query: $query}' | curl -s -X POST "http://localhost:3000/graphql" \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  --data @-)
echo "$CREATE_RESPONSE" | jq
```

Use the **unquoted** delimiter `<<GRAPHQL` only when the operation must interpolate a previously exported shell variable (for example `$SMOKE_RECORD_ID`):

```bash
UPDATE_QUERY=$(cat <<GRAPHQL
mutation {
  updateRecord(
    id: "$SMOKE_RECORD_ID"
    data: {
      dynamicFields: {
        rich_text: "<p>Tag @[<user_id>]</p>"
      }
    }
  ) {
    id
    dynamicFields
  }
}
GRAPHQL
)
UPDATE_RESPONSE=$(jq -n --arg query "$UPDATE_QUERY" '{query: $query}' | curl -s -X POST "http://localhost:3000/graphql" \
  -H "Content-Type: application/json" \
  -H "Authorization: $TOKEN" \
  --data @-)
echo "$UPDATE_RESPONSE" | jq
```

Rules for `curl`-based GraphQL blocks:

- Always assign the operation to a `*_QUERY` variable using `cat <<'GRAPHQL' ... GRAPHQL` (quoted) by default.
- Switch to the unquoted `<<GRAPHQL` delimiter **only** when shell interpolation of an exported variable is required, and explicitly state the interpolated variable in the surrounding step.
- Always build the request body with `jq -n --arg query "$VAR" '{query: $query}'` instead of hand-escaping quotes.
- Split `curl` flags across lines with `\` continuations: one flag per line for `-H "..."`, with `--data @-` on the last line.
- Capture the response into a `*_RESPONSE` variable and pipe it through `| jq` on the next line so the tester can read the JSON output.

#### Rails runner scripts

Do **not** generate `bundle exec rails runner '...'` one-liners with semicolons stitching multiple statements. Use the stdin form with a `RUBY` heredoc so each statement and each step of a query chain is on its own line:

```bash
bundle exec rails runner - <<'RUBY'
record_id = ENV.fetch("SMOKE_RECORD_ID")

mentions = Mention
  .where(record_id: record_id, origin: :text)
  .order_by(column_id: :asc)
  .pluck(:referenceable_type, :referenceable_id, :column_id)
  .map { |type, referenceable_id, column_id| [type, referenceable_id.to_s, column_id.to_s] }

puts mentions.inspect
RUBY
```

Rules for `rails runner` blocks:

- Always invoke as `bundle exec rails runner - <<'RUBY' ... RUBY` (quoted delimiter) so the script reads from stdin and `$` characters stay literal.
- Fetch ENV vars first, on their own lines.
- Break Mongoid/ActiveRecord query chains across `.where`, `.order_by`, `.pluck`, `.map`, etc., with each link starting on its own indented line under the receiver.
- Assign the result to a named local (for example `mentions`, `summary`) and `puts` it on a separate final line. Do not inline `puts({ ... }.inspect)`.
- When building a multi-key summary hash, declare the hash on its own block of lines before the `puts`.

#### General one-liner avoidance

Beyond GraphQL and `rails runner`, the same readability rule applies to any shell command that strings together multiple steps. If a command:

- chains 3 or more pipeline stages with non-trivial logic, or
- contains escaped quotes inside escaped quotes, or
- mixes setup, action, and assertion in a single statement,

then split it into a heredoc, a `*_QUERY`/`*_PAYLOAD` variable, or sequential lines so each step is independently readable. Prefer clarity over compactness in `SMOKE_TEST.md`.

---

## Step 5 — Review For Accuracy

Before finishing, verify that:

- every scenario maps back to code or tests in the diff
- every prerequisite is necessary and explained
- every step has an observable expected result
- the file does not require hidden tribal knowledge
- the instructions help a human validate the branch manually, not inspect internals

If the branch changes multiple surfaces, order the scenarios from most important to least important.

---

## Step 6 — Final Output

Write `SMOKE_TEST.md`, then show the user:

- the provided `BASE_REF`
- whether a `Pre-requisites` section was included
- a short summary of the scenarios covered
