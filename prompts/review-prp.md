---
allowed-tools: Bash,Glob,Grep,Read,TodoWrite,WebFetch,WebSearch,firecrawl_scrape,firecrawl_search,firecrawl_crawl,firecrawl_extract
description: Review existing PRP for a given task to ensure they are accurate, complete, and optionally improve them
argument-hint: issue_id
---

PRP file: $ARGUMENTS

## Step 1: Review PRP

Review the PRP to ensure:
- it addresses the stated need/task/feature detailed in the main issue description
- it is accurate and complete in regard to the current state of the codebase

If there are any issues with the PRP (gaps in understanding, unclear requirements, erroneous assumptions), proactively investigate and ask clarifying questions to ensure the specs are accurate and complete.

## Step 3: List specs improvements (if needed)

If the specs can be improved, give a clear and concise list of the improvements that can be made to the PRP.
