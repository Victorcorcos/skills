---
name: coverager
description: 'Increase code coverage to 100% by analyzing a SimpleCov HTML coverage report, identifying uncovered lines, and writing meaningful BDD-structured tests avoid mocking our classes and methods and focusing on real user journeys and scenarios. Use when asked to increase coverage, fill coverage gaps, or reach 100% test coverage. Requires a path to the SimpleCov index.html file as input.'
---

# 📈 Coverager

> **Purpose**: Analyze a SimpleCov HTML coverage report, identify files and lines with missing coverage, and write meaningful, BDD-structured automated tests that exercise those code paths — reaching 100% coverage without resorting to lazy or artificial test padding.

---

## Input

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `FILE_PATH` | Yes | — | Path to the SimpleCov `index.html` coverage report. Pass as the first argument: `/coverager path/to/coverage/index.html`, `$coverager path/to/coverage/index.html`. |

If the user does not provide a file path, ask for it before proceeding.

---

## Testing Guidelines (from BDDer)

The tests created by this skill **must** follow these principles. Coverage is a side-effect of good tests, not the goal itself.

### Philosophy

User-centric testing principles ensure all tests are meaningful from the user's perspective.

Tests must simulate **user journeys or user scenarios** — sequences of actions a real user would perform — rather than testing individual methods or internal class behavior in isolation.

### Structure

Tests must prioritize clarity, consistency, and maintainability. Write tests for people to read, not machines to execute.

### Real-world Testing

Favor real-world interactions over mocks and stubs. **Avoid mocking our own classes and methods.** Internal code paths must be exercised for real; only mock at the true system boundary (external HTTP APIs, hardware, environment).

---

## Step 1 — Extract Uncovered Lines

Run the extraction script to identify which files and lines are missing coverage:

```bash
python3 "$SKILLS_PATH/skills/coverager/scripts/extract_uncovered.py" "<FILE_PATH>"
```

If `SKILLS_PATH` is not set, try these fallback paths in order:

1. `skills/coverager/scripts/extract_uncovered.py` (when working inside the skills repository)
2. `~/.codex/skills/coverager/scripts/extract_uncovered.py` (common for Codex CLI installs)

Print the full output to screen so the developer can see which files and lines need coverage.

If the script reports **"All files have 100% coverage!"**, inform the developer and stop.

---

## Step 2 — Analyze Uncovered Code

For each file with missed lines, read the **full source file** (not just the uncovered lines) to understand:

1. **Context**: What does this file do? What is its role in the application?
2. **Uncovered paths**: What scenarios trigger the missed lines? Are they error handlers, edge cases, conditional branches, or entire features?
3. **Existing tests**: Find the corresponding test file(s). What scenarios are already covered? What is missing?
4. **Dependencies**: What setup (factories, fixtures, database state, external services) is needed to exercise the uncovered paths?

Group the uncovered lines by **user scenario**, not by file order. Each group should map to a meaningful test scenario that a real user or system interaction would trigger.

---

## Step 3 — Plan Test Scenarios

For each group of uncovered lines, design test scenarios that follow BDD principles:

### Scenario Design Rules

- **Test user journeys, not lines**: Do not write a test whose sole purpose is to execute a specific line. Instead, identify the user scenario that *naturally* exercises those lines.
- **One scenario per behavior**: Each test scenario should cover one coherent behavior, not a grab-bag of unrelated lines.
- **Happy path + edge cases**: Cover the happy path first, then error states and edge cases.
- **Real interactions**: Exercise the full stack where possible. For controllers, use request specs. For models, use real database interactions. For helpers, call them with realistic inputs.
- **Mock only at boundaries**: Only mock external HTTP APIs, third-party services, hardware, or environment-level interactions. Never mock internal classes or methods.

### Present the Plan

Before writing any test, present the plan to the developer:

```
## Coverage Plan

### File: <filepath> (N lines uncovered)

Scenario 1 — "<describe the user scenario>"
  Covers lines: <line numbers>
  Test type: <request spec / model spec / helper spec / etc.>
  Setup needed: <factories, fixtures, external mocks>

Scenario 2 — "<describe the user scenario>"
  Covers lines: <line numbers>
  Test type: <request spec / model spec / helper spec / etc.>
  Setup needed: <factories, fixtures, external mocks>

[repeat for each file]
```

Wait for the developer to approve or adjust the plan before proceeding.

---

## Step 4 — Apply BDD Structure

Write all tests following this strict BDD structure:

### `describe()` blocks — Describe scenarios

Use subordinating conjunctions to frame the context:

- Start with: `when`, `after`, `while`, `with`
- Examples:
  - `"when the user submits an empty form"`
  - `"after the database is seeded with users"`
  - `"with multiple filters applied"`
  - `"while the session is expired"`

Nest `describe` blocks to express progressively narrower scenarios. Each level narrows the context without repeating parent context.

### `before()`/`before(:all)`/`beforeAll`/`beforeETC` blocks — Prepare the scenario

Use `before` related blocks exclusively for setup. Never put assertions inside them.

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

**Never mock our own classes or methods.** Internal implementations must be exercised for real so that tests reflect genuine user journeys rather than artificial call chains. Mocking internal code hides bugs and makes tests brittle when implementation details change.

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

Apply these improvements across all new test files:

### Clarity
- Remove redundant comments that just restate the code
- Ensure test names are unique, self-explanatory and intention-revealing without needing to read the body

### Consistency
- Use the same factory/fixture style already established in the project
- Match naming conventions observed in the existing test suite
- Align indentation and formatting with the rest of the file

### Coverage
- Identify any obvious gaps: what scenario is clearly missing?
- Add missing `it` blocks for edge cases visible from the uncovered lines (e.g., nil inputs, empty collections, boundary values)
- Cover the happy path first, then error states

### Assertions
- One primary assertion per `it` block (secondary assertions for closely related attributes are acceptable)
- Assert against meaningful values, not just truthiness (`expect(user.email).to eq("test@example.com")` not `expect(user.email).to be_truthy`)
- Avoid asserting implementation details — assert observable outcomes

---

## Step 7 — Write the Tests

Apply all changes directly to the test files. Do not create separate files or leave TODOs.

When adding tests to existing spec files:
- Place new `describe`/`context` blocks in a logical position within the file
- Follow the existing file's conventions for factories, let blocks, shared examples, etc.

When creating new spec files:
- Follow the project's directory structure (e.g., `spec/requests/`, `spec/models/`, `spec/helpers/`)
- Include the standard requires and setup used by other spec files in the project

After writing:
- Read the file back and verify the BDD structure is correct
- Verify no existing test logic was accidentally removed or broken
- Verify each `describe` block has at least one `it` block

---

## Step 8 — Run the Tests

Run only the changed/new test files to confirm they pass:

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

If tests **fail after writing**, diagnose and fix the issue before reporting. Do not leave broken tests.

If tests **cannot be run** (missing environment, missing DB, etc.), note this clearly in the output.

---

## Step 9 — Verify Coverage Improvement

After all tests pass, re-run the coverage report and then re-run the extraction script:

```bash
python3 "$SKILLS_PATH/skills/coverager/scripts/extract_uncovered.py" "<FILE_PATH>"
```

Compare the before and after:
- Which files moved to 100%?
- Which lines are still uncovered? Why?
- If lines remain uncovered and cannot be reasonably tested (e.g., dead code, unreachable branches), flag them for the developer.

---

## Step 10 — Report

After all improvements are applied, produce a short summary:

```
## Coverager Summary 📈

### Before
- Total coverage: XX.XX%
- Files with gaps: N
- Lines missed: M

### After
- Total coverage: YY.YY%
- Files with gaps: N'
- Lines missed: M'

### Tests Created/Modified

#### File: path/to/spec_file.rb (new / modified)
- Added N scenarios covering lines X-Y of <source_file>
- Scenarios: <brief list of scenario descriptions>

#### File: path/to/another_spec.rb (new / modified)
- Added N scenarios covering lines X-Y of <source_file>
- Scenarios: <brief list of scenario descriptions>

[...]

### Remaining Gaps (if any)
- <filepath>: lines X, Y — <reason they cannot be tested>

### Tests Status
All tests pass  /  Could not run (reason)
```

Keep the report concise. No full file dumps — just what changed and why.
