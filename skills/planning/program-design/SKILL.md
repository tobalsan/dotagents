---
name: program-design
description: Design the shape of the code before any implementation—call-stack trees, file-tree diffs, and key types/method signatures—drafted for the user to argue with. Use after a plan/spec/PRD exists and before breaking work into issues or coding. Triggers on "/program-design", "program design", "design the code shape", "sketch the call stacks/signatures", "what should the types look like", or when the user wants a code-level design pass on an approved plan. NOT for requirements interviewing (drill-specs), writing the PRD (to-prd), creating tickets (to-issues), or implementing.
---

# Program Design

Go one level below architecture into the **shape of code**: types, method signatures, program layout, and call stacks. Every artifact produced here is a decision that would otherwise be made implicitly during code review—the most expensive time to change your mind.

## Input

A settled plan: PRD, spec, architecture doc, or the current conversation context. If the user passes a doc/issue reference as `$ARGUMENTS`, fetch and read it fully.

## Process

### 1. Ground in the codebase

Explore the code the change touches (subagents in parallel). Existing conventions win: reuse current types, module layout, and naming. A design that ignores the codebase's current shape just moves the argument to code review.

### 2. Draft the visualizations

Draft, don't interview. Produce light pseudocode visualizations—not prose paragraphs, not mermaid (it lures you into false alignment). Three forms:

**Call-stack tree** — for any orchestration or control-flow change. Use diff syntax when the interesting part is what's changing:

```diff
 entrypoint
   runCommand
+    handleCreateResource
+      ResourceClient.create(input)
+        POST /resources
+      renderResult
-    legacyCreateFlow
```

**File-tree diff** — so the layout of the codebase and where stuff lives stays visible:

```diff
 src
 └── resource
+    ├── resource-client.ts      # NEW — wraps API contract calls
+    ├── resource-client.test.ts # NEW — covers request/response mapping
~    └── resource-route.ts       # MODIFIED — wires create action into UI
```

**Types & method signatures** — for the key new functions: the stuff too internal for an architecture doc but that an implementer (human or agent) could still get wrong. Skeletons only, no bodies:

```ts
interface Cursor {
  position: ItemId
  direction: 'up' | 'down'
}

resolveTarget(items: Item[], cursor: Cursor) -> ItemId | null
```

Skip any form that doesn't apply (a pure schema migration may need no call-stack tree). Where two shapes are plausible, show both with a recommendation—don't pick silently.

### 3. Argue with the user

Present the draft and invite pushback: wrong layer boundaries? types too wide/narrow? call stack too deep? files in the wrong place? Iterate until the user approves. This is the whole point—these artifacts take minutes to produce and the user's arguments are the value.

### 4. Record

Append the approved design as a "Program Design" section on the source doc (PRD/spec/issue), or write it to `./docs/specs/`, per user preference.

## Rules

- **Design only.** Do NOT implement, and do NOT write function bodies.
- **Stay at the shape level.** Error-handling minutiae, exact copy, styling—out of scope unless they change a signature.
- **Keep it short.** The whole design should read in a few minutes; if it doesn't fit on roughly one screen per visualization, the slice is too big—say so.
- **Done when** an implementer could write the code without making any structural decision themselves: no new files, types, or call paths beyond what's drawn here.
