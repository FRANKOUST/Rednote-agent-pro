## Why

Collected Xiaohongshu posts only become useful when the platform can extract repeatable patterns and convert them into actionable content directions. Analysis and topic generation must be explicit platform capabilities so later draft generation is grounded in evidence rather than generic prompting.

## What Changes

- Add analysis jobs that derive high-frequency keywords, title patterns, tag usage, and user insight summaries from collected posts.
- Persist structured analysis reports tied to source post sets and crawl jobs.
- Generate topic suggestions with titles, rationale, and source evidence.
- Expose report and topic outputs to later drafting workflows and operator interfaces.

## Capabilities

### New Capabilities

- `content-pattern-analysis`: Structured extraction of content patterns from collected source posts.
- `topic-suggestion-generation`: AI-assisted topic generation grounded in analysis outputs.
- `analysis-report-storage`: Persistent storage and retrieval of analysis reports and topic suggestions.

### Modified Capabilities

None.

## Impact

- Affects application services, LLM provider usage, persistence, and downstream draft generation inputs.
- Introduces structured prompt design, output validation, and traceability from topics back to evidence.
