---
name: improver
description: 'Review changed code on the current branch for Clean Code, security, performance, test quality, and repository/framework convention issues, then walk the user through each finding one by one with proposed fixes and interactive approval. Use when asked to improve, review and fix, or audit code quality on a branch.'
---

# ✨ Improver

> **Purpose**: Analyze the diff of the current branch against the base branch, identify Clean Code violations, security vulnerabilities, performance issues, test quality weaknesses, and repository/framework convention mismatches, then walk the user through each finding one by one — proposing a fix, showing the diff, and asking for approval before applying it.

Here is the desired workflow of this task in detail.

---

## Non-Negotiables

- **One issue at a time**: NEVER fix multiple issues in a single step. Each finding must be presented, discussed, and resolved individually before moving to the next.
- **Always use `AskUserQuestion` tool**: When asking the user whether to apply a fix, you MUST use the `AskUserQuestion` tool with structured options. Do NOT present options as plain text and wait for a freeform response.
- **No code changes before approval**: Do NOT apply any fix until the user has explicitly selected an option via the `AskUserQuestion` tool response.

---

## Step 1 — Resolve the Diff Base

Before anything else, ensure git references are up-to-date and then resolve a diff base.

### Prerequisites

First, update all remote references to ensure they match the latest state:

```bash
git fetch --all --prune
```

This command:
- Fetches updates from all remotes (`upstream` and `origin`)
- Removes local references to deleted remote branches (`--prune`)
- Ensures the fallback chain below finds valid, current references

**Important**: Without this step, the branch resolution may fail if the local git database is stale.

### Resolve the diff base

**Fallback chain** for the diff base — try each in order until one succeeds:
1. `upstream/main`
2. `upstream/master`
3. `origin/main`
4. `origin/master`

Store whichever works as `BASE_REF` and use it throughout.

```bash
BASE_REF=""
for ref in upstream/main upstream/master origin/main origin/master; do
  git rev-parse --verify --quiet "$ref" >/dev/null && BASE_REF="$ref" && break
done

test -n "$BASE_REF" && echo "$BASE_REF"
```

Then collect the full diff:

```bash
git diff "$BASE_REF"
```

And the list of changed files:

```bash
git diff "$BASE_REF" --name-only
```

---

## Step 2 — Understand Context

### Read the changed files

Read every changed file **in full** (not just the diff hunks) to understand context. You need the surrounding code to judge whether something is truly an issue.

### Read the related automated tests

For every changed implementation file, locate and read the most relevant automated tests even if the tests were not changed in this branch.

- Prefer the closest matching test file by name, module, or feature area
- Read existing tests for the same feature, service, controller, model, hook, component, or endpoint
- If the branch already changes tests, read those test files in full as first priority
- If you cannot find any relevant tests for a changed behavior, treat that as potential `Test Quality` evidence rather than silently ignoring it

You must evaluate whether the implementation is actually covered by automated tests, not just whether test files exist.

### Read repository conventions

Read `README.md`, `AGENTS.md`, and `CLAUDE.md` at the repository root (if they exist). These files define the project's conventions, architecture decisions, and coding standards. You will need them for the Convention category in Step 3.

### Read sibling files for convention discovery

For each changed file, **read 1–3 similar files** in the same directory or module. For example:

- If the branch touches `src/services/userService.ts`, also read other files in `src/services/` (e.g., `orderService.ts`, `paymentService.ts`).
- If the branch touches `app/models/user.rb`, also read other models in `app/models/`.
- If the branch touches a test file, read other test files in the same test directory.

This lets you discover the **actual patterns the codebase uses** — naming conventions, error handling style, import ordering, class structure, decorator usage, etc. — so you can flag deviations in the changed code.

### Align with the repository's BDD testing standard

When tests are present or should be added, apply the same core BDD expectations used by the `bdder` skill:

- `describe` blocks should describe scenarios or contexts such as `when`, `with`, `after`, `while`
- `before`-style hooks should prepare the scenario, not contain assertions
- `it` blocks should describe outcomes and ideally start with `should`
- Tests should prefer real user journeys and observable behavior over implementation-detail assertions
- Mocks and stubs should be limited to external APIs, external libraries, time, hardware, filesystem, environment boundaries, or similarly unavoidable seams
- Internal classes, methods, and collaborators should usually be exercised through real flows instead of being heavily mocked

---

## Step 3 — Analyze the Changed Code

For each changed file, identify issues in **five categories**:

1. **Code Smell** — Clean Code violations, maintainability problems
2. **Security** — Vulnerabilities, unsafe patterns
3. **Performance** — Inefficiencies, resource waste
4. **Test Quality** — Missing, weak, brittle, over-mocked, or non-BDD automated tests
5. **Convention** — Repository/framework alignment violations

Use the reference tables below as your checklist for categories 1–4. For category 5 (Convention), use what you learned from reading `README.md`, `AGENTS.md`, `CLAUDE.md`, and sibling files in Step 2.

However, **the tables are just a starting point** — you can and should flag issues that go beyond what is cataloged in the tables.

> **Important**: Focus exclusively on code introduced or modified in this branch. Do not flag pre-existing issues in unchanged code unless they are directly affected by the new changes.

### What to look for in each category

**Code Smell**: See Table A. Look for long methods, duplicate code, deep nesting, dead code, naming issues, SRP/DRY/KISS violations, overengineering, etc.

**Security**: See Table B. Look for injection risks, hardcoded credentials, broken access control, cryptographic misuse, unsafe deserialization, etc.

**Performance**: See Table C. Look for N+1 queries, missing indexes, memory leaks, blocking I/O, unbounded results, excessive DOM manipulation, etc.

**Test Quality**: See Table D. Inspect the implementation and its related tests together. Look for:
- changed lines that are untested or only incidentally executed without a meaningful assertion
- missing tests for newly introduced or materially changed behavior
- missing happy path, failure path, branch, boundary, and common edge-case coverage
- tests that claim coverage but only assert superficial outcomes while missing the real feature behavior
- tests that overuse mocks/stubs for internal classes or methods, creating false confidence instead of real scenario coverage
- tests that verify implementation details instead of user-visible or externally observable outcomes
- tests that violate the BDD structure above and the conventions used by the repository's existing test suite
- flaky or brittle tests caused by incidental timing, shared state, random ordering, or poor isolation
- missing regression tests for bugs fixed by the branch

Treat lack of test coverage as a first-class finding when the branch changes behavior, data flow, branching logic, error handling, or integrations in a way that should be protected by automated tests.

**Convention**: No table — this is based on what you observed in the repository. Look for:
- File naming patterns that differ from sibling files (e.g., `kebab-case.ts` where the repo uses `PascalCase.ts`, or `user_service.py` where the repo uses `userService.py`); also check pluralization/singularization (e.g., `users.ts` vs `user.ts`) and whether the file is placed in the correct folder according to the codebase's conventions and good practices (e.g., a service placed in `controllers/`, or a model placed in `utils/`)
- Class, method, and variable naming patterns that differ from sibling files (e.g., camelCase where the repo uses snake_case)
- Structural patterns that differ (e.g., logic in a controller when the repo puts it in services)
- Import/require ordering that differs from the established style
- Error handling approaches that differ from sibling files
- Missing or extra decorators, annotations, or middleware compared to similar files
- Framework idiom violations (e.g., using raw SQL when the repo uses an ORM everywhere)
- Contradictions with rules stated in `README.md`, `AGENTS.md`, or `CLAUDE.md`

---

## Step 4 — Build the Findings Report

For each issue found, record:

| Field | Description |
|-------|-------------|
| **#** | Sequential number |
| **Category** | `Code Smell`, `Security`, `Performance`, `Test Quality`, or `Convention` |
| **Severity** | `Critical`, `High`, `Medium`, or `Low` |
| **File** | File path and line number(s) |
| **Issue** | Short description of what is wrong |
| **Why it matters** | One sentence explaining the impact |
| **Proposed fix** | Description of the recommended change |

Present all findings to the user as a numbered summary table:

```
## Findings Summary

| # | Category | Severity | File | Issue |
|---|----------|----------|------|-------|
| 1 | Security | Critical | src/auth.ts:42 | Hardcoded API key |
| 2 | Code Smell | Medium | src/utils.ts:15 | Long method (87 lines) |
| 3 | Performance | High | src/db.ts:23 | N+1 query in loop |
| 4 | Test Quality | High | spec/api_spec.rb:55 | Missing regression test for invalid token flow |
| 5 | Convention | Medium | src/api.ts:8 | Uses raw SQL; repo convention is ORM |
| ... | ... | ... | ... | ... |

I found [N] issues. Let's walk through each one.
```

Sort findings by severity: Critical > High > Medium > Low.

If **no issues are found**, report that clearly and stop:

> "I reviewed the changes on this branch and found no code smells, security issues, performance problems, test quality issues, or convention mismatches. The code looks good!"

---

## Step 5 — Interactive Fix-by-Fix Walkthrough

Process each finding **one at a time** in the following cycle:

```
┌──────────────────────────────────────────────────────┐
│  1. Announce: "Issue #N of M — [Category] [Severity]"│
│  2. Show the current problematic code                 │
│  3. Explain why it is a problem                       │
│  4. Show the proposed fix (as a diff when possible)   │
│  5. Ask the user for their decision                   │
└──────────────────────────────────────────────────────┘
```

### Decision prompt — MUST use AskUserQuestion tool

After showing the proposed fix, you **MUST** use the `AskUserQuestion` tool to collect the user's decision. Do NOT simply print the options as text and wait — you MUST invoke the tool.

Always use these two options:

1. `label: "Apply fix"`, `description: "[one-line description of the fix]"`
2. `label: "Skip"`, `description: "Move to the next issue without changes"`

The question text must follow this format:
> `"Issue #N — [Short description]: apply this fix?"`

Set `header` to `"Issue #N"` and `multiSelect` to `false`.

The user can always select "Other" (automatically provided by the tool) to explain what they want instead.

### Handling each option

- **Apply fix**: Apply the fix to the code immediately. Confirm it was applied and move to the next issue.
- **Skip**: Acknowledge the skip and move to the next issue. Do not apply any change.
- **Other** (user typed a custom response): Read the user's explanation. Propose a revised fix based on their feedback. Show the updated diff. Ask again with the `AskUserQuestion` tool using the same structure. Repeat until the user picks a solution or skips.

### Additional rule for `Test Quality` findings

When the finding is in `Test Quality`, prefer fixing the automated tests themselves.

- If existing tests are weak, improve those tests instead of only changing production code
- If relevant tests are missing and the repository patterns are clear, add the missing tests as part of the fix
- If tests are over-mocked, replace internal mocks/stubs with more realistic setup where feasible
- If BDD structure is weak, rewrite the tests to follow the repository's scenario-based style
- If the implementation itself is hard to test because of poor seams, you may propose a minimal production-code change, but keep the focus on enabling stronger real-world tests
- After applying a `Test Quality` fix, run the smallest relevant test command you can determine from the repository

### Between issues

After applying or skipping an issue, move to the next one:

> "Moving to issue #[N+1] of [M]..."

---

## Step 6 — Final Report

After all issues have been addressed, present a summary:

```
## Improvement Complete

### Applied Fixes
- ✅ #1 — [Short description]
- ✅ #3 — [Short description]

### Skipped
- ⏭️ #2 — [Short description] (user chose to skip)

### Stats
- Total issues found: [M]
- Fixes applied: [X]
- Skipped: [Y]
```

---

## Reference Tables

The tables below are your checklists for categories 1–4. Use them to identify issues in the analyzed code. Not every item will apply to every codebase — only flag what is **actually present** in the changed code.

**Remember**: These tables are a starting point, not an exhaustive list. If you spot an issue that is not in these tables but is clearly a problem, flag it anyway.

---

### Table A — Code Smells & Clean Code

| Smell | Reason | Solution |
|-------|--------|----------|
| **Long Method** | Hard to read, test, debug, and reuse. Violates Single Responsibility Principle and increases cognitive load. | Extract smaller, focused methods with clear names. Apply "one level of abstraction per function" rule. |
| **God Class (Large Class)** | Centralizes unrelated logic, becomes a bottleneck for changes, difficult to test in isolation. | Apply SRP. Extract cohesive subsets of fields and methods into separate classes. Delegate responsibilities. |
| **Duplicate Code** | Every bug fix or change must be applied in all locations. Missing one introduces inconsistencies and bugs. | Extract into a shared method or class. Apply DRY. Use inheritance or composition to unify common behavior. |
| **Long Parameter List** | Hard to call correctly, easy to invoke with wrong argument order, signals method is doing too much. | Introduce a Parameter Object. Use Preserve Whole Object. Apply builder or fluent interface patterns. |
| **Primitive Obsession** | Raw primitives for domain concepts prevent validation, encapsulation, and semantic clarity. | Replace with value objects or domain types (Money, PhoneNumber). Use enums for fixed sets. |
| **Feature Envy** | A method accesses another class's data more than its own — logic lives in the wrong place. | Move the method to the class whose data it most uses. Apply Tell Don't Ask. |
| **Data Clumps** | Groups of variables always appear together — represent an unnamed concept. Error-prone to pass individually. | Extract the clump into a dedicated class or value object. |
| **Switch Statements** | Large switch/if-else chains violate Open/Closed Principle. Every new case requires modifying existing code. | Replace conditionals with polymorphism. Use Strategy or State pattern. |
| **Divergent Change** | A single class modified for many unrelated reasons — multiple responsibilities tangled together. | Separate along lines of change. Extract Class so each has one reason to change. |
| **Shotgun Surgery** | One logical change requires modifying many different classes. Makes changes fragile and expensive. | Move Method and Move Field to consolidate related behavior into a single class. |
| **Speculative Generality** | Code for future requirements that don't exist adds complexity and dead abstractions. | Delete unused abstractions. Apply YAGNI. Inline unnecessary delegation. |
| **Dead Code** | Never-executed code clutters the codebase, misleads developers, increases maintenance burden. | Delete it — version control preserves history. Use static analyzers to detect unreachable paths. |
| **Magic Numbers / Magic Strings** | Literal values carry no meaning, must be duplicated, easy to modify incorrectly. | Replace with named constants or enums with descriptive names. |
| **Inappropriate Intimacy** | Two classes constantly access each other's internals — too tightly coupled. | Move methods/fields to reduce bidirectional dependencies. Use interfaces. |
| **Message Chains** | Call chains like `a.getB().getC().getD()` expose internal structure and couple client to every intermediate type. | Apply Law of Demeter. Use Hide Delegate to encapsulate the traversal. |
| **Middle Man** | A class that only delegates to another adds indirection with no value. | Inline the class. Call the real object directly. |
| **Lazy Class** | A class that does very little introduces complexity without benefit. | Inline its contents into its caller or parent. Remove if no distinct value. |
| **Data Class** | A class with only fields, getters, setters and no behavior — anemic domain model. | Move behavior into the class. Apply Tell Don't Ask. Enrich the domain model. |
| **Refused Bequest** | Subclass inherits but doesn't use most parent methods — wrong inheritance relationship. | Replace inheritance with composition/delegation. |
| **Parallel Inheritance Hierarchies** | Every new subclass in one hierarchy requires a corresponding one in another. | Merge hierarchies. Use Strategy or Visitor patterns. |
| **Temporary Field** | Instance variable only used in certain situations, clutters the class for its entire lifetime. | Extract into a separate class or use local variables. |
| **Deep Nesting (Hadouken IFs)** | Multiple nesting levels exponentially increase cyclomatic complexity and mental load. | Apply guard clauses / early returns. Extract nested blocks. Invert conditions to flatten structure. |
| **Negative Conditionals** | Negative conditions (`!isNotValid`) increase cognitive strain and are error-prone to reason about. | Rewrite as positive conditionals. Use well-named boolean methods (`isValid`). |
| **Flag Arguments** | Boolean parameters make call sites opaque (`render(true)` — true means what?). | Split into two named methods. Replace booleans with enums or descriptive strings. |
| **Excessive Comments** | Comments compensating for unclear code. They go stale and become misleading. | Refactor to be self-explanatory: extract named methods, rename variables, simplify logic. |
| **Global Data** | Global variables / singletons readable and writable from anywhere — hidden dependencies, hard to test. | Encapsulate behind a controlled interface. Use dependency injection. |
| **Mutable Data** | Data changeable from any location introduces hidden coupling and unpredictable state. | Apply immutability. Use value objects. Isolate mutations to narrow locations. |
| **Inconsistent Naming** | Different names for the same concept force developers to learn multiple synonyms. | Establish and enforce a project-wide naming convention and ubiquitous language. |
| **Indecent Exposure** | Making internal details public allows external code to depend on internals that should be free to change. | Make everything private unless there is an explicit reason to expose it. |
| **Anemic Domain Model** | Domain objects with only data and all logic in service classes — procedural code disguised as OOP. | Move logic from services into domain objects. Apply Tell Don't Ask. |

---

### Table B — Security Issues

| Name | Risk | Solution |
|------|------|----------|
| **SQL Injection** | 5/5 | Use parameterized queries / prepared statements. Apply ORMs with strict binding. Validate and sanitize all user input. Enforce least-privilege DB accounts. |
| **Cross-Site Scripting (XSS)** | 5/5 | Encode all output contextually (HTML, JS, CSS, URL). Apply Content Security Policy (CSP) headers. Use templating engines with auto-escape. |
| **Broken Access Control** | 5/5 | Enforce server-side authorization on every request. Implement RBAC/ABAC. Deny by default. Audit access logs. |
| **OS Command Injection** | 5/5 | Avoid calling OS commands from application code. Use language-native APIs. If unavoidable, whitelist allowed commands and arguments. Never pass unsanitized input to shells. |
| **Remote Code Execution (RCE)** | 5/5 | Keep software patched. Disable dangerous features (eval, exec). Sandbox execution. Apply strict input validation. |
| **Buffer Overflow / Out-of-Bounds Write** | 5/5 | Use memory-safe languages. Apply compiler protections (stack canaries, ASLR, bounds checking). Run static analysis. |
| **Use-After-Free** | 5/5 | Use memory-safe languages or smart pointers. Apply static and dynamic analysis. Enable AddressSanitizer during testing. |
| **Cryptographic Failures** | 5/5 | Use strong modern algorithms (AES-256, RSA-2048+, TLS 1.2+). Never use MD5/SHA-1 for security. Encrypt at rest and in transit. Manage keys in vaults. |
| **Broken Authentication** | 5/5 | Enforce MFA. Use secure session management with short-lived tokens. Rate-limit and lock out after failures. Hash passwords with bcrypt/Argon2. |
| **Insecure Deserialization** | 5/5 | Avoid deserializing untrusted data. Use safe formats (JSON with schema validation). Implement integrity checks (HMAC). Run in sandboxed environments. |
| **Path Traversal** | 4/5 | Canonicalize and validate file paths server-side. Use allow-lists for directories. Never concatenate user input directly into file paths. |
| **Server-Side Request Forgery (SSRF)** | 4/5 | Validate and sanitize user-supplied URLs. Enforce allowlists for outbound destinations. Block internal IP ranges. Use network segmentation. |
| **XML External Entity (XXE)** | 4/5 | Disable external entity processing in XML parsers. Use JSON instead. Keep XML libraries patched. |
| **Security Misconfiguration** | 4/5 | Use hardened minimal configurations. Automate configuration management (IaC). Remove default credentials and unused features. |
| **Vulnerable / Outdated Components** | 4/5 | Maintain an SBOM. Monitor dependencies for CVEs with SCA tools. Automate updates. Remove unused libraries. |
| **Insecure Direct Object Reference (IDOR)** | 4/5 | Enforce authorization on every object access server-side. Use indirect references (GUIDs). Implement access control tests in CI/CD. |
| **Cross-Site Request Forgery (CSRF)** | 4/5 | Use anti-CSRF tokens. Apply SameSite cookie attributes. Verify Origin/Referer headers. |
| **Hardcoded Credentials** | 4/5 | Never embed secrets in source code. Use secrets managers. Scan repos with GitGuardian/truffleHog. Rotate credentials on discovery. |
| **Privilege Escalation** | 4/5 | Apply least privilege. Enforce strict RBAC. Audit sudo/SUID. Patch OS/kernel vulnerabilities. |
| **Improper Input Validation** | 4/5 | Validate all input server-side using strict type, length, format, and range checks. Use allowlists over denylists. Reject malformed input early. |
| **Insecure Design** | 4/5 | Integrate threat modeling early. Apply secure design patterns. Conduct security architecture reviews. |
| **Software / Data Integrity Failures** | 4/5 | Verify integrity via cryptographic signatures. Use trusted registries. Implement CI/CD pipeline security. Apply SRI for client-side assets. |
| **Supply Chain Attacks** | 4/5 | Vet dependencies carefully. Use pinning and lockfiles. Monitor for dependency confusion. Use signed packages. |
| **Sensitive Data Exposure** | 4/5 | Classify data by sensitivity. Encrypt PII at rest and in transit. Apply data masking in non-production. Enforce strict access controls. |
| **Session Management Failures** | 4/5 | Regenerate session IDs after login. Use secure, HttpOnly, SameSite cookie flags. Set short timeouts. Enforce HTTPS. |
| **Insufficient Logging / Monitoring** | 3/5 | Log authentication events, access control failures, validation errors. Centralize in SIEM. Set up real-time alerts. |
| **Integer Overflow / Underflow** | 3/5 | Use safe arithmetic libraries. Validate numeric ranges. Use compiler warnings and static analysis. |
| **Open Redirect** | 3/5 | Use allowlists of permitted redirect destinations. Resolve targets server-side using internal IDs. |
| **Clickjacking** | 3/5 | Set X-Frame-Options to DENY/SAMEORIGIN. Use frame-ancestors CSP directive. |
| **Race Condition / TOCTOU** | 3/5 | Use atomic operations and DB transactions with proper locking. Use mutexes for shared resource access. |
| **Mass Assignment** | 3/5 | Whitelist allowed fields in model binding. Use DTOs. Apply strict schema validation. |
| **Business Logic Flaws** | 3/5 | Conduct workflow abuse threat modeling. Enforce server-side business rules. Test negative/edge-case scenarios. |

---

### Table C — Performance Issues

| Name | Risk | Solution |
|------|------|----------|
| **N+1 Query Problem** | 5/5 | Use eager loading (ORM `includes`/`joinedload`). Batch queries with dataloaders. Rewrite to a single JOIN query. |
| **Missing Database Indexes** | 5/5 | Analyze slow query logs and EXPLAIN plans. Add indexes on WHERE, JOIN, ORDER BY columns. Avoid over-indexing write-heavy tables. |
| **Memory Leaks** | 5/5 | Audit for unclosed resources, lingering listeners, static collections. Use profilers (Chrome DevTools, Eclipse MAT, tracemalloc). |
| **Blocking I/O on Async Event Loops** | 5/5 | Never call synchronous blocking operations in async coroutines. Offload to thread pool (`run_in_executor`, worker threads). |
| **Cache Stampede / Thundering Herd** | 5/5 | Apply mutex so only one request regenerates cache. Use probabilistic early expiration. Stagger TTLs and implement request coalescing. |
| **Connection Pool Exhaustion** | 5/5 | Right-size pool limits. Fix leaks by ensuring connections are returned. Use PgBouncer/HikariCP for pool management. |
| **Unbounded Task Queues** | 5/5 | Replace with bounded queues. Apply backpressure. Monitor queue depth in production. |
| **Inefficient Algorithms (Poor Complexity)** | 4/5 | Profile hot paths. Replace O(n^2) with hash maps, sorting, or divide-and-conquer. Choose appropriate data structures. |
| **Long-Running Database Transactions** | 4/5 | Keep transactions short. Move non-DB work outside boundaries. Use row-level locking and statement timeouts. |
| **Excessive Lock Contention / Deadlocks** | 4/5 | Prefer fine-grained locks. Use optimistic locking for low-contention. Acquire locks in consistent global order. |
| **Thread Pool Misconfiguration** | 4/5 | Separate CPU-bound and I/O-bound pools. Size CPU pool to cores. Measure throughput and tune. |
| **Over-Indexing (Index Bloat)** | 4/5 | Audit for unused/duplicate indexes. Remove redundant ones. Periodically rebuild fragmented indexes. |
| **Chatty Microservices** | 4/5 | Aggregate in API Gateway or BFF. Batch fine-grained requests. Use async messaging to decouple services. |
| **Retry Storms** | 4/5 | Apply exponential backoff with jitter. Set max retry limits. Implement circuit breakers. |
| **Resource Leaks (Handles, Sockets)** | 4/5 | Use try-with-resources (Java), context managers (Python), `using` (C#). Run static analysis in CI. |
| **Excessive DOM Manipulation / Layout Thrashing** | 4/5 | Batch DOM reads before writes. Animate with `transform`/`opacity`. Use `DocumentFragment` for bulk inserts. Virtualize long lists. |
| **SELECT * / Over-Fetching Data** | 3/5 | Select only needed columns. Restrict API responses to required fields. Consider GraphQL for diverse field requirements. |
| **ORM Lazy Loading Misuse** | 3/5 | Identify lazy associations in loops. Switch to eager loading or explicit JOINs. Use read-model projections for complex queries. |
| **Lack of Response Caching** | 3/5 | Cache query results and API responses in Redis/Memcached. Set appropriate TTLs. Use HTTP cache headers (ETag, Cache-Control). |
| **Unoptimized Images / Static Assets** | 3/5 | Compress with modern formats (WebP, AVIF). Serve responsive sizes. Lazy load below-the-fold content. Minify and bundle CSS/JS. |
| **Excessive / Verbose Logging** | 3/5 | Restrict DEBUG/TRACE to non-production. Use async log handlers. Avoid serializing large objects in logs. Sample at high traffic. |
| **Large Payload Serialization** | 3/5 | Avoid transmitting excess data. Use binary formats (Protobuf, MessagePack) internally. Stream large payloads. |
| **Catastrophic Regex Backtracking** | 3/5 | Audit nested quantifiers (`(a+)+`). Use possessive quantifiers or atomic groups. Test against adversarial input. Enforce timeouts. |
| **Missing HTTP Compression** | 3/5 | Enable gzip or Brotli on server/gateway for text responses. Verify with response headers. |
| **Lack of Pagination** | 3/5 | Never return unbounded result sets. Implement cursor-based or offset pagination. Apply LIMIT in queries. Use virtual scrolling on client. |
| **Excessive Third-Party Scripts** | 3/5 | Audit with Lighthouse/WebPageTest. Load non-critical scripts with `async`/`defer`. Self-host critical third-party resources. |
| **Polling Instead of Push** | 2/5 | Replace with webhooks, WebSockets, or SSE for real-time updates. If unavoidable, use long-polling with exponential backoff. |
| **Serverless Cold Starts** | 2/5 | Keep packages small. Use provisioned concurrency (Lambda SnapStart, Azure always-ready). Prefer fast-startup runtimes (Python, Node.js). |
| **Hot Partitions in Distributed DBs** | 2/5 | Design partition keys with high cardinality. Add random suffix jitter. Cache hot partitions. Monitor per-partition metrics. |
| **Lack of CDN for Static Content** | 2/5 | Serve static assets through CDN edge nodes. Configure long cache TTLs with content-hash filenames. Enable HTTP/2. |

---

### Table D — Test Quality Issues

| Name | Why it matters | What good looks like |
|------|----------------|----------------------|
| **Untested Changed Lines** | A diff can look covered while the newly introduced lines are never asserted in a meaningful way. | Ensure the changed lines participate in a scenario with assertions that would fail if those lines behaved incorrectly. |
| **Missing Tests For Changed Behavior** | New or changed behavior can regress immediately with no automated signal. | Add or update tests that exercise each meaningful behavior introduced by the diff. |
| **Missing Happy Path Coverage** | The main user journey is unprotected, so the feature may not work at all despite passing CI. | Add a straightforward scenario proving the intended feature works end to end at the appropriate test level. |
| **Missing Failure / Error Path Coverage** | Error handling often breaks silently and causes user-facing failures in production. | Add tests for invalid input, dependency failures, permission failures, and expected error states relevant to the diff. |
| **Missing Branch Coverage** | Conditionals and branching logic can hide untested behavior on one side of the decision. | Cover each meaningful branch introduced or modified by the implementation. |
| **Missing Boundary / Edge Case Coverage** | Bugs usually surface at limits such as empty, nil, zero, duplicate, max-size, or out-of-range inputs. | Add tests for the common edge cases implied by the implementation and domain. |
| **Missing Regression Test** | A bug fix without a regression test is likely to reappear later. | Add a failing-then-passing test that captures the exact bug or previously broken scenario. |
| **Over-Mocked Internal Behavior** | Heavy mocking of your own classes and methods creates false confidence and fragile tests that track implementation, not behavior. | Mock only real external boundaries and use real internal flows, factories, fixtures, and collaborators whenever practical. |
| **Testing Implementation Details** | Tests become brittle and fail during harmless refactors while missing real user impact. | Assert observable outputs, state transitions, side effects, rendered UI, HTTP responses, persisted data, and domain events. |
| **Non-BDD Structure** | Poor naming and setup structure makes tests hard to read, reason about, and maintain. | Use scenario-based `describe` blocks, `before` for setup, focused `it should` outcomes, and clear nested contexts. |
| **Scattered Setup Inside Assertions** | Tests become noisy and each example reimplements the scenario differently. | Centralize setup in shared helpers or `before` blocks and keep `it` blocks focused on assertions. |
| **Assertion Weakness** | Superficial assertions let incorrect behavior slip through while still producing green tests. | Assert concrete, meaningful outcomes instead of generic truthiness or call-count trivia. |
| **Flaky / Non-Deterministic Tests** | Unstable tests erode trust in the suite and slow down delivery. | Control time, randomness, ordering, and shared state explicitly so the same inputs produce the same results. |
| **Wrong Test Level** | Too-low-level tests miss real feature behavior; too-high-level tests can be slow and vague. | Choose the smallest level that still proves the real user scenario or business behavior changed by the diff. |
| **Unclear Scenario Naming** | Test names stop acting as executable documentation. | Describe the scenario and outcome in plain language that another engineer can scan quickly. |
---

## Quality Principles

These principles apply throughout the review:

- **Evidence-based**: Only flag issues you can point to in the actual code. Never fabricate or speculate.
- **Severity-honest**: Rate issues by real impact, not to inflate the findings count.
- **One at a time**: Never batch-apply fixes. Each fix needs explicit user approval.
- **Minimal changes**: Fix only the identified issue — do not refactor surrounding code unless the user asks.
- **Context-aware**: Respect existing codebase conventions. Propose fixes that match the project's style.
- **No silent changes**: Never modify code without showing the user what will change first.
- **Beyond the tables**: The reference tables are a starting point. Flag any real issue you find, even if it is not listed in the tables.
- **Test realism over line coverage theater**: Do not stop at "some lines are executed." Prefer tests that prove real feature behavior, real branches, and common edge cases with minimal internal mocking.
