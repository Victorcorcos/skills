---
name: reviewer
description: 'Review changed code on the current branch for Clean Code, security, performance, and repository/framework convention issues, then walk the user through each finding one by one. Instead of applying fixes locally, post approved findings as inline PR comments (with code suggestions when applicable) on the associated GitHub pull request. Use when asked to review a PR and leave comments, or to post review feedback on GitHub.'
---

# Reviewer

> **Purpose**: Analyze the diff of the current branch against the base branch, identify Clean Code violations, security vulnerabilities, performance issues, and repository/framework convention mismatches, then walk the user through each finding one by one — and for each approved finding, post an inline comment on the associated GitHub pull request (with a code suggestion when applicable) instead of modifying local files.

Here is the desired workflow of this task in detail.

---

## Step 1 — Resolve the Diff Base and PR Info

Before anything else, resolve the diff base, obtain the changed code, and identify the associated pull request.

### Resolve the diff base

**Fallback chain** — try each in order until one succeeds:
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

### Collect the diff

```bash
git diff "$BASE_REF"
```

And the list of changed files:

```bash
git diff "$BASE_REF" --name-only
```

### Identify the pull request

You need the PR number and the HEAD commit SHA to post review comments. Run:

```bash
gh pr view --json number,headRefOid
```

This returns something like:

```json
{
  "number": 42,
  "headRefOid": "abc123def456..."
}
```

Store `number` as `PR_NUMBER` and `headRefOid` as `HEAD_SHA`. You will need both in Step 5.

If no PR exists for the current branch, tell the user:

> "No open pull request found for this branch. Please create a PR first, or use the `improver` skill to apply fixes locally instead."

Then stop.

---

## Step 2 — Understand Context

### Read the changed files

Read every changed file **in full** (not just the diff hunks) to understand context. You need the surrounding code to judge whether something is truly an issue.

### Read repository conventions

Read `README.md`, `AGENTS.md`, and `CLAUDE.md` at the repository root (if they exist). These files define the project's conventions, architecture decisions, and coding standards. You will need them for the Convention category in Step 3.

### Read sibling files for convention discovery

For each changed file, **read 1–3 similar files** in the same directory or module. For example:

- If the branch touches `src/services/userService.ts`, also read other files in `src/services/` (e.g., `orderService.ts`, `paymentService.ts`).
- If the branch touches `app/models/user.rb`, also read other models in `app/models/`.
- If the branch touches a test file, read other test files in the same test directory.

This lets you discover the **actual patterns the codebase uses** — naming conventions, error handling style, import ordering, class structure, decorator usage, etc. — so you can flag deviations in the changed code.

---

## Step 3 — Analyze the Changed Code

For each changed file, identify issues in **four categories**:

1. **Code Smell** — Clean Code violations, maintainability problems
2. **Security** — Vulnerabilities, unsafe patterns
3. **Performance** — Inefficiencies, resource waste
4. **Convention** — Repository/framework alignment violations

Use the reference tables below as your checklist for categories 1–3. For category 4 (Convention), use what you learned from reading `README.md`, `AGENTS.md`, `CLAUDE.md`, and sibling files in Step 2.

However, **the tables are just a starting point** — you can and should flag issues that go beyond what is cataloged in the tables.

> **Important**: Focus exclusively on code introduced or modified in this branch. Do not flag pre-existing issues in unchanged code unless they are directly affected by the new changes.

### What to look for in each category

**Code Smell**: See Table A. Look for long methods, duplicate code, deep nesting, dead code, naming issues, SRP/DRY/KISS violations, overengineering, etc.

**Security**: See Table B. Look for injection risks, hardcoded credentials, broken access control, cryptographic misuse, unsafe deserialization, etc.

**Performance**: See Table C. Look for N+1 queries, missing indexes, memory leaks, blocking I/O, unbounded results, excessive DOM manipulation, etc.

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
| **Category** | `Code Smell`, `Security`, `Performance`, or `Convention` |
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
| 4 | Convention | Medium | src/api.ts:8 | Uses raw SQL; repo convention is ORM |
| ... | ... | ... | ... | ... |

I found [N] issues. Let's walk through each one.
For approved issues, I will post inline comments on PR #[PR_NUMBER].
```

Sort findings by severity: Critical > High > Medium > Low.

If **no issues are found**, report that clearly and stop:

> "I reviewed the changes on this branch and found no code smells, security issues, performance problems, or convention mismatches. The code looks good!"

---

## Step 5 — Interactive Review-by-Review Walkthrough

This is the most important step. Process each finding **one at a time** in the following cycle:

```
┌──────────────────────────────────────────────────────────┐
│  1. Announce: "Issue #N of M — [Category] [Severity]"     │
│  2. Show the current problematic code                      │
│  3. Explain why it is a problem                            │
│  4. Show the proposed PR comment (including code           │
│     suggestion if applicable)                              │
│  5. Ask the user for their decision                        │
└──────────────────────────────────────────────────────────┘
```

### How to ask the user

After showing the proposed comment, you **MUST** use the AI tool's built-in question/prompt mechanism to present the user with selectable options. Do NOT just print text and wait for free-form input — use the tool's native option-selection feature (e.g., `AskUserQuestion` in Claude Code, or equivalent in Codex CLI / OpenCode).

Present exactly these three options:

> **Issue #N — [Short description]**
>
> Do you want to post this comment on the PR?
> 1. **Yes** — Post the comment on the PR and move to the next issue
> 2. **No** — Skip this issue and move to the next one
> 3. **Other** — Explain your concern or suggest a different approach

### Handling each option

- **Yes**: Post the inline comment on the PR immediately (see "How to post comments" below). Confirm it was posted. Move to the next issue.
- **No**: Acknowledge the skip. Do NOT post anything. Move to the next issue.
- **Other**: Read the user's feedback. Propose a revised comment based on their input. Show the updated comment. Ask again with the same three options. Repeat until the user chooses **Yes** or **No**.

### Between issues

After posting or skipping an issue, move to the next one:

> "Moving to issue #[N+1] of [M]..."

---

## How to Post Comments on the PR

### Option A — Inline comment on a specific line (preferred)

Use this when the issue is tied to a specific line or range of lines in the diff. This posts an inline review comment directly on the affected code.

**Single-line comment** (the issue is on one line):

```bash
gh api repos/{owner}/{repo}/pulls/$PR_NUMBER/comments \
  -f body='**[Category] [Severity]**: [Issue title]

[Explanation of why this is a problem]

**Suggested fix:**
```suggestion
[the corrected code for that line]
```' \
  -f commit_id="$HEAD_SHA" \
  -f path='[file path]' \
  -f line=[line number] \
  -f side='RIGHT'
```

**Multi-line comment** (the issue spans multiple lines):

```bash
gh api repos/{owner}/{repo}/pulls/$PR_NUMBER/comments \
  -f body='**[Category] [Severity]**: [Issue title]

[Explanation of why this is a problem]

**Suggested fix:**
```suggestion
[the corrected code replacing all lines from start_line to line]
```' \
  -f commit_id="$HEAD_SHA" \
  -f path='[file path]' \
  -f start_line=[first line number] \
  -f start_side='RIGHT' \
  -f line=[last line number] \
  -f side='RIGHT'
```

### Option B — General PR comment (fallback)

Use this **only** when the issue is not tied to a specific line (e.g., a missing file, an architectural concern, a convention mismatch about folder structure).

```bash
gh pr comment $PR_NUMBER --body '**[Category] [Severity]**: [Issue title]

[Explanation of why this is a problem and how to fix it]'
```

### Comment formatting rules

Every PR comment must follow this structure:

1. **Header**: `**[Category] [Severity]**: [Issue title]` — so the PR author can quickly scan the comment type.
2. **Explanation**: Why this is a problem, with context. Be concise but clear.
3. **Code suggestion** (when applicable): Use GitHub's `` ```suggestion `` block so the PR author can apply the fix with one click. The suggestion block **must contain the exact replacement code** for the lines specified by `line` (or `start_line` to `line` range).

### Important rules for suggestions

- The content inside `` ```suggestion `` must be the **complete replacement** for the line(s) you target. GitHub will replace lines `start_line` through `line` with whatever is inside the suggestion block.
- If the fix is to **delete** code, use an empty suggestion block: `` ```suggestion\n``` ``
- If the fix is to **add** code, include the original line(s) plus the new code in the suggestion.
- If the fix cannot be expressed as a simple line replacement (e.g., "split this 80-line method into 3 methods"), **do not** use a suggestion block. Instead, describe the fix in prose and let the author implement it.
- Always verify the `line` number refers to the line in the **new version** of the file (right side of the diff), not the old version.

### How to determine line numbers

The `line` parameter must be a line number in the **new version** of the file that appears in the diff. To find the correct line numbers:

1. Look at the diff output from Step 1.
2. Find the `@@` hunk headers (e.g., `@@ -10,5 +12,7 @@`). The `+12,7` part means this hunk starts at line 12 in the new file.
3. Count from there: line 12, 13, 14, etc.
4. Only lines that appear in the diff (additions `+` and context lines ` `) can be commented on. Lines that only appear as deletions (`-`) cannot be targeted.

---

## Step 6 — Final Report

After all issues have been addressed, present a summary:

```
## Review Complete

### Posted to PR #[PR_NUMBER]
- ✅ #1 — [Short description]
- ✅ #3 — [Short description]

### Skipped
- ⏭️ #2 — [Short description] (user chose to skip)

### Stats
- Total issues found: [M]
- Comments posted: [X]
- Skipped: [Y]
```

---

## Reference Tables

The tables below are your checklists for categories 1–3. Use them to identify issues in the analyzed code. Not every item will apply to every codebase — only flag what is **actually present** in the changed code.

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

## Quality Principles

These principles apply throughout the review:

- **Evidence-based**: Only flag issues you can point to in the actual code. Never fabricate or speculate.
- **Severity-honest**: Rate issues by real impact, not to inflate the findings count.
- **One at a time**: Never batch-post comments. Each comment needs explicit user approval.
- **No local changes**: This skill posts PR comments — it does NOT modify local files. Use the `improver` skill if you want to apply fixes locally.
- **Context-aware**: Respect existing codebase conventions. Propose fixes that match the project's style.
- **No silent posts**: Never post a PR comment without showing the user what will be posted first.
- **Beyond the tables**: The reference tables are a starting point. Flag any real issue you find, even if it is not listed in the tables.
