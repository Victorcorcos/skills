---
name: bdder
description: 'Analyze changed tests in the current branch and improve them using Behavior Driven Development principles. Use when asked to rewrite, restructure, or improve tests in a BDD style with readable, meaningful, and real-world focused test cases.'
---

# 🧪 BDDer

> **Purpose**: Analyze the current branch diff, find created/changed automated tests, and improve them using Behavior Driven Development principles — making tests readable, meaningful, and real-world focused.

---

## Step 1 — Resolve Diff Base

Resolve the diff base using the same fallback chain as other skills:

```bash
BASE_REF=""
for ref in upstream/main upstream/master origin/main origin/master; do
  git rev-parse --verify --quiet "$ref" >/dev/null && BASE_REF="$ref" && break
done

test -n "$BASE_REF" && echo "$BASE_REF"
```

Store whichever works as `BASE_REF` and use it throughout.

---

## Step 2 — Find Changed Test Files

Extract only the test-related files from the diff:

```bash
git diff "$BASE_REF" --name-only | grep -E "(spec|test|__tests__|_test|\.test\.|\.spec\.)"
```

If **no test files changed**, inform the user:

> "No test files were found in this diff. Nothing to improve."

Then stop. Do not proceed.

If test files are found, read each one fully before making any changes.

---

## Step 3 — Analyze Existing Tests

For each changed test file, analyze:

1. **Structure**: Are tests grouped by scenario or by function? Are nested contexts used?
2. **Naming**: Do `describe` blocks describe *scenarios*? Do `it` blocks describe *outcomes*?
3. **Setup**: Is setup scattered inside `it` blocks, or cleanly isolated in `before` blocks?
4. **Realism**: Are mocks/stubs used where real interactions are possible?
5. **Clarity**: Can a non-author read the test and understand what it covers?
6. **Coverage**: Are happy paths covered? Edge cases? Error states?
7. **Assertions**: Are assertions meaningful and minimal (one concern per `it`)?

---

## Step 4 — Apply BDD Structure

Restructure and improve each test file following these rules:

### `describe()` blocks — Describe scenarios

Use subordinating conjunctions to frame the context:

- Start with: `when`, `after`, `while`, `with`
- Examples:
  - `"when the user submits an empty form"`
  - `"after the database is seeded with users"`
  - `"with multiple filters applied"`
  - `"while the session is expired"`

Nest `describe` blocks to express progressively narrower scenarios. Each level narrows the context without repeating parent context.

### `before()`/`before(:all)` blocks — Prepare the scenario

Use `before` blocks exclusively for setup. Never put assertions inside them.

- Create records, configure state, render components
- Declare important variables (e.g., `@user`, `@result`, `@response`)
- Execute the action under test (e.g., call the method, trigger the event)

### `it()` blocks — Assert specific outcomes

Each `it` block tests one thing and one thing only.

- Start with: `"should"`
- Examples:
  - `"should display a validation error"`
  - `"should redirect to the dashboard"`
  - `"should not create a duplicate record"`

Do not put setup or multi-step interactions inside `it` blocks. Keep them as pure assertions.

### Nesting pattern

```
describe "when <scenario>" do
  before do
    # prepare scenario
  end

  it "should <outcome>" do
    # assert outcome
  end

  describe "when <narrower scenario>" do
    before do
      # refine state or perform additional action
    end

    it "should <outcome>" do
      # assert narrowed outcome
    end
  end
end
```

---

## Step 5 — Eliminate Mocks and Stubs

Favor real-world interactions over mocks and stubs wherever possible.

**Remove or replace:**
- Mocked method calls that could use actual implementations
- Stubbed return values for internal logic
- Fake objects where real factory/fixture objects can be used

**Keep only when unavoidable:**
- External HTTP calls (third-party APIs, webhooks)
- Time-sensitive code (`Time.freeze` is acceptable)
- Hardware, filesystem, or environment-level interactions with no reasonable alternative

When replacing a mock with a real interaction, ensure the test still isolates its concern — use database transactions or cleanup hooks to avoid cross-test pollution.

---

## Step 6 — Improve Test Quality

Apply these improvements across all changed test files:

### Clarity
- Remove redundant comments that just restate the code
- Remove dead or skipped tests (`xit`, `xdescribe`, `pending`) unless they are intentionally skipped with a tracked reason
- Ensure test names are unique and self-explanatory without needing to read the body

### Consistency
- Use the same factory/fixture style already established in the project
- Match naming conventions observed in the existing test suite
- Align indentation and formatting with the rest of the file

### Coverage
- Identify any obvious gaps: what scenario is clearly missing?
- Add missing `it` blocks for edge cases visible from the diff (e.g., nil inputs, empty collections, boundary values)
- Cover the happy path first, then error states

### Assertions
- One primary assertion per `it` block (secondary assertions for closely related attributes are acceptable)
- Assert against meaningful values, not just truthiness (`expect(user.email).to eq("test@example.com")` not `expect(user.email).to be_truthy`)
- Avoid asserting implementation details — assert observable outcomes

---

## Step 7 — Write Improved Tests

Apply all changes directly to the test files. Do not create separate files or leave TODOs.

After rewriting:
- Read the file back and verify the BDD structure is correct
- Verify no test logic was accidentally removed
- Verify each `describe` block has at least one `it` block

---

## Step 8 — Run the Tests

Run only the changed test files to confirm they pass:

```bash
# Detect test runner from the project
# Ruby/RSpec
bundle exec rspec <changed_test_files>

# JavaScript/Jest
npx jest <changed_test_files>

# Python/pytest
pytest <changed_test_files>

# Go
go test ./...

# Generic fallback — adapt to the project's test command
```

If tests **fail after restructuring**, diagnose and fix the issue before reporting. Do not leave broken tests.

If tests **cannot be run** (missing environment, missing DB, etc.), note this clearly in the output.

---

## Step 9 — Report

After all improvements are applied, produce a short summary:

```
## BDD Improvements Applied

### Files Changed
- path/to/spec_file.rb
- path/to/another_spec.js

### Changes Made
- Restructured `describe` blocks to use scenario-based naming
- Moved inline setup into `before` blocks
- Replaced 3 mocks with real ActiveRecord interactions
- Added 2 missing edge case tests for <scenario>
- Fixed 1 assertion that tested implementation detail

### Tests Status
✅ All tests pass  /  ⚠️ Could not run (reason)
```

Keep the report concise. No full file dumps — just what changed and why.
