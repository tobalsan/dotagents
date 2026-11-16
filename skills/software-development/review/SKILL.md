---
name: review
description: Design and test-quality review of a PR, branch, diff or code area, on top of the usual correctness review. Checks that tests are behavioral, that code follows SOLID and KISS, flags premature abstraction, needless coupling and duplicated responsibilities, and checks that feature work lands as vertical slices in deep modules. Use when asked to review a PR, a diff, a branch or code in general, on "/review", or when acting as a reviewer agent.
metadata:
  origin: "self"
---

# Review

This skill adds a design and test pass to your normal review. Keep doing what a review already covers (correctness, security, edge cases, fit with the stated goal). Then run the four checks below and report them in the same output.

## Companion skills

Four sibling skills may be installed next to this one, at `../<name>/SKILL.md` relative to this file. They may also be absent. If one is available, read it before the check it supports. If it is not, the checklist below is enough on its own. Use them as reference: do not start their interactive workflows (reports, interviews, edits) during a review.

- **codebase-design**: the deep-module vocabulary (module, interface, depth, seam, adapter, deletion test). Read it for checks 3 and 4.
- **improve-codebase-architecture**: how to spot shallow modules and deepening opportunities. Read it when a finding reaches beyond the diff.
- **refactor**: code smells and the refactorings that fix them. Use it to name a smell and propose the smallest fix.
- **simplify-code**: clarity, redundancy, needless complexity. Read it for the KISS part of check 2.

## Before the checks

1. **Scope.** Establish what you are reviewing: a PR, a branch diff (`git diff <base>...HEAD`), working-tree changes, or a code area the caller names. Read the surrounding code you need to judge it.
2. **Intent.** Read the PR description or issue. Decide if the change delivers a feature (a new user-facing or caller-facing capability). Only feature work gets check 4.
3. **Conventions.** Note how the repo is organised (by feature or by layer) and any architecture docs or ADRs. Judge the change against them, and say so when a finding conflicts with an existing convention.
4. **Pre-existing problems.** Flag them only when the change touches or worsens them, and label them `pre-existing`.

## Check 1: tests are behavioral

A good test describes a behavior through a public interface. Ask two questions of each new or changed test:

- **Refactor-proof?** If the implementation were rewritten with the same behavior, would the test still pass? If not, it is structure-dependent.
- **Bug-catching?** If the behavior broke, would the test fail? If not, it is tautological or empty.

Flag as **tautological**, and name the bug that would slip through:
- The expected value is derived with the same logic as the code under test (e.g. the test re-runs the pricing formula to get the expected total), so a bug in that logic appears on both sides. Expected values should come from an independent source: a literal, a worked example, the spec.
- The expected value is taken from the actual result, or a value is compared with itself.
- A mock is set to return X and the test asserts X came back, with no real logic in between.
- A new or updated snapshot whose content you cannot match to the intended behavior.
- The test would still pass if the feature were deleted.

Flag as **structure-dependent** when the test is tied to details outside the module's contract:
- It mocks internal collaborators instead of system edges (network, clock, third-party APIs, sometimes the filesystem).
- It asserts call counts, call order or arguments of internal functions.
- It tests private methods, or reads state through a side channel (querying the database directly instead of using the interface).
- It asserts on class names, file layout or internal data shapes.

Context decides: a database read is fine when persistence is the contract under test, and a module's own tests may use its internal seams. Flag only when the test would break under a behavior-preserving refactor.

Also flag **missing tests**: new behavior with no test, or a bug fix with no test that reproduces the bug.

## Check 2: SOLID and KISS

Look for concrete tells, not textbook violations:

- **Single responsibility**: a function or module with more than one independent reason to change, e.g. a request handler that also holds pricing rules another feature edits. A cohesive feature module that parses, decides and persists for one capability is not a violation.
- **Open/closed**: adding a new case means editing the same `switch` or `if` chain in several places.
- **Liskov**: an implementation that throws "not implemented", ignores arguments or accepts less than its contract; callers that check the concrete type.
- **Interface segregation**: callers forced to depend on methods or options they never use; fat interfaces and option bags.
- **Dependency inversion**: business logic that builds its own infrastructure (creates its HTTP client or database connection inside), so it cannot be tested without patching.
- **KISS**: indirection that adds a hop and nothing else; configuration for things that never vary; generic code that serves one case; clever one-liners; deep nesting that guard clauses would flatten.

SOLID applied by rote creates the abstractions check 3 flags. When there is one variant and no second in sight, KISS wins. Flag over-engineering done in the name of SOLID as readily as a SOLID violation.

## Check 3: premature abstraction, coupling, duplicated responsibility

**Premature abstraction**
- An interface, base class, factory, strategy or plugin point with one implementation and no concrete second one planned.
- Generic parameters, hooks or options that no caller varies; code "for future use".
- Test it with the deletion test: inline the abstraction in your head. If complexity vanishes, it was premature. If complexity reappears across callers, the abstraction earns its keep even with one implementation. One adapter is a hypothetical seam; two adapters make a real one.

**Unnecessary coupling**
- A module that reaches into another module's internals or private state.
- A change that forces edits in modules unrelated to its goal.
- Types of a dependency leaking through an interface, so callers must know that dependency.
- Shared mutable state, circular imports, hidden ordering rules ("call `init` before `run`").

**Duplicated responsibility**
- Two places validate, compute or own the same rule; state held in two places that can drift apart.
- A new helper that re-implements something the codebase already has. Search for it (similar names, similar logic) before you flag or clear it.
- Do not flag incidental similarity: code that looks alike but changes for different reasons should stay separate.

## Check 4: feature work lands as vertical slices in deep modules

Skip this check for refactors, infrastructure, dependency bumps and pure bug fixes. Say it was skipped and why.

Expected shape: a vertical slice. The slice may cross tiers (UI, API, storage), but one module (or a small set) owns the feature's rules end to end, behind a small interface. That module is **deep**: a lot of behavior behind a small interface.

How to check:
1. Group the touched files by directory or domain, then trace where the feature's rules and decisions live.
2. Ask: could this feature be removed by deleting one module or folder, plus its wiring?
3. Ask: is each new module's interface small next to what it does? A layer that only passes calls through is shallow.

Flag as **horizontal**, with the concrete cost (scattered rules, extra edits per change, shallow handoffs):
- The feature's rules are split across transverse layers (a bit in `controllers/`, `services/`, `repositories/`, `types/`, `utils/`), each piece shallow.
- Feature logic is put into a cross-cutting module (`utils`, `helpers`, `common`, a shared "manager") that other domains also use.
- One change mixes several unrelated domains.

Directory names alone are not a finding. In a repo layered by convention or by ADR, flag only scattered rules or shallow pass-through layers, as a suggestion, not a blocker. Do not ask for a re-architecture inside one PR. Point to the smallest step toward a slice.

## Findings and severity

Every finding needs evidence: a location (`path:line`), what is wrong, which check it fails, a concrete consequence, and the smallest fix. No evidence, no finding. Put open assumptions in a separate "Questions" list, not among the findings.

Set severity from the demonstrated impact:

- **Blocker**: the main new behavior has no meaningful test; a design flaw with a concrete cost that will be hard to undo after merge (a public interface or data shape that callers will depend on); duplicated rules that already disagree or will drift into bugs.
- **Should fix**: a contained design problem that is cheap to fix now and costly later.
- **Nit**: local style or naming; mark it optional.

Do not pad. Do not invent a finding for a check that passes.

## Output

If your caller or agent instructions set a review format or severity scale, use it and fit these findings into it; add the check summary only if that format has room for it. Otherwise:

```
Verdict: approve | request changes | comment

Blockers
- [Tests: tautological] src/cart.test.ts:42. The expected total is computed with the same formula as the code, so a wrong discount rule passes. Fix: assert against a worked example (3 items, 10% off = 27.00).

Should fix
- ...

Nits
- ...

Questions
- ...

Checks: tests ✓ | SOLID/KISS 1 finding | abstraction/coupling/duplication ✓ | vertical slices n/a (bug fix)
```

In this default format the `Checks` line is required: it shows that all four checks ran, including the ones that passed. Mark a check `not assessed` if you could not run it, and say why.
