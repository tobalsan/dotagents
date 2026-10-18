---
description: Review committed changes in the context of a given Linear issue.
---

Focus: $ARGUMENTS

## Step 1: Understand the broader context

Review the parent project or scope and identify:
- Where this issue fits in the overall feature/epic
- What has already been completed (earlier implementations)
- What is intentionally deferred to later / other issues

This prevents flagging "gaps" that are actually scoped for subsequent issues.

## Step 3: Review changes

List the recent commits and identify those that are related to the issue (most likely the last commit).

Review the changes introduced, and assess the relevance, accuracy, and completeness of the implementation.
We're not looking for the most perfect implementation, but rather a solid and well-executed one. Look for:
- Gaps 
- Inconsistencies
- Erroneous assumptions
- Crucial oversights
- Speculative code
- Unnecessary abstractions

Keep in mind: our principles are simplicity, pragmatism, effectiveness, and elegance over perfection.
If an implementation is fine as is, let it be.

Present a final report of your findings, whether your assessment is positive or negative, and add it as a comment on the issue.

